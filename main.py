from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
import uvicorn
import asyncio
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()   # 启动时从 .env 读取密钥注入环境变量

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),   # 从环境变量读，代码里不再出现明文密钥
)

app = FastAPI(docs_url=None)


class PydanticModel(BaseModel):
    code: str
    name: str
    alert_price: float


class CommentRequest(BaseModel):
    code: str
    question: str


class ReportRequest(BaseModel):
    code: str
    question: str


@app.get("/docs", include_in_schema=False)
def custom_docs():
    # 用国内 CDN 镜像加载文档页面，解决默认 jsdelivr 白屏问题
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="盯盘助手 - API 文档",
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui.css",
    )

@app.get("/")
def read_root():
    return {"msg": "你好，我是盯盘助手后端"}

@app.get("/ping")
def ping():
    return{"status":"ok"}

@app.get("/hello")
def hello():
    return{"say": "欢迎使用盯盘助手"}

@app.get("/hello/{name}")
def hello_name(name: str):
    return {"hello": name, "msg": "欢迎使用盯盘助手"}

@app.get("/news")
def get_news(limit: int = 3, tag: str = "ALL"):
    return {"limit": limit, "tag": tag}

@app.post("/watch")
def watch_stock(stock: PydanticModel):
    return {"added": stock.code, "name": stock.name, "alert": stock.alert_price}

def chat_once(question: str) -> str:
    # ① 剧本：system 定角色 + user 是问题
    messages = [
        {"role": "system", "content": "你是盯盘助手，用简洁中文回答"},
        {"role": "user",   "content": question},
    ]
    # ② 流式调用
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
    )
    # ③ 循环拼碎片
    answer = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            answer += delta
    return answer


@app.post("/comment")
async def comment(req: CommentRequest):
    try:
        # 用 f-string 把股票代码和问题拼成一句话喂给大模型
        prompt = f"股票{req.code}：{req.question}"
        answer = await asyncio.to_thread(chat_once, prompt)
        return {"code": req.code, "answer": answer}
    except Exception as e:
        return {"error": str(e)}


@app.post("/report")
async def report(req: ReportRequest):
    try:
        # 步骤A：先拉真实行情（同步 requests，用 to_thread 包住不卡循环）
        quote = await asyncio.to_thread(fetch_quote, req.code)
        # 步骤B：把"名称 + 当前价 + 用户问题"拼成有依据的 prompt
        prompt = f"股票{quote['name']}({req.code}) 当前价 {quote['price']} 元。{req.question}"
        # 步骤C：把带真价的 prompt 交给大模型点评
        answer = await asyncio.to_thread(chat_once, prompt)
        return {"code": req.code, "name": quote["name"],
                "price": quote["price"], "answer": answer}
    except Exception as e:
        return {"error": str(e)}


def fetch_quote(prefix_code: str) -> dict:
    # prefix_code 形如 "sh600519"（沪市 sh / 深市 sz）
    url = f"https://qt.gtimg.cn/q={prefix_code}"
    r = requests.get(url, timeout=10)
    r.encoding = "gbk"                       # 腾讯返回 GBK，不设中文名就乱码
    body = r.text.split('"')[1]              # 取出引号里的内容
    parts = body.split("~")                  # 用 ~ 切字段
    return {"code": prefix_code, "name": parts[1], "price": float(parts[3])}


@app.get("/prices/{codes}")
async def prices(codes: str):
    async def get_price(prefix_code: str):
        return await asyncio.to_thread(fetch_quote, prefix_code)   # 同步→线程池
    results = await asyncio.gather(*[get_price(c) for c in codes.split(",")])
    return {"prices": results}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="debug",
    )
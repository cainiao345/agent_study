# 盯盘助手后端（S2 验收项目）

基于 **FastAPI** 的行情点评后端服务：提供自选股真实行情接口，并接入大模型（OpenAI 兼容接口）对行情做一句话点评或问答。是「Agent 工程化」学习路线 S2 阶段的验收项目。

> 同仓库还包含 S1 阶段验收项目 `stock_crawler.py`（定时行情抓取脚本），可独立运行。

## 功能特性
- 📈 **真实行情**：通过腾讯财经免 key 接口获取自选股实时价格（沪市 `sh` / 深市 `sz`）。
- 🤖 **大模型点评**：接入 DeepSeek（OpenAI 兼容）对单只股票做基于真实价格的问答/点评。
- ⚡ **异步并发**：多只股票行情并发拉取，同步 I/O 用线程池托管不阻塞事件循环。
- 🔐 **密钥安全**：API key 走环境变量 + `.env`，绝不进代码、不进 Git。
- 📚 **可调试**：内置 `/docs` 交互式文档（国内 CDN 镜像，告别白屏）。

## 环境要求
- Python 3.9+
- 已安装 `venv`（创建虚拟环境用）

## 安装与配置
```bash
# 1. 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥：在项目根目录新建 .env 文件，写入
DEEPSEEK_API_KEY=你的DeepSeek密钥
```
> ⚠️ `.env` 已被 `.gitignore` 忽略，密钥不会上传。请到 DeepSeek 开放平台获取 key。

## 运行
```bash
uvicorn main:app --reload
```
启动后访问：
- API 文档：`http://127.0.0.1:8001/docs`
- 健康检查：`http://127.0.0.1:8001/ping`

## API 接口说明

### GET /prices/{codes}
并发获取多只自选股的真实行情（逗号分隔，沪市前缀 `sh`、深市前缀 `sz`）。
- 请求示例：`GET /prices/sh600519,sz000001`
- 返回示例：
```json
{
  "prices": [
    {"code": "sh600519", "name": "贵州茅台", "price": 1335.0},
    {"code": "sz000001", "name": "平安银行", "price": 11.2}
  ]
}
```

### POST /comment
把股票代码 + 问题交给大模型做点评（模型不直接知道行情，适合开放性提问）。
- 请求体：
```json
{"code": "sh600519", "question": "这家公司基本面怎么样"}
```
- 返回示例：
```json
{"code": "sh600519", "answer": "贵州茅台是国内白酒龙头……"}
```
- 缺字段返回 `422`（Pydantic 自动校验）。

### POST /report
**闭环接口**：先拉取真实行情 → 再把「名称 + 当前价 + 问题」交给大模型点评（模型基于真实价格作答）。
- 请求体：
```json
{"code": "sh600519", "question": "当前估值高吗，值得关注吗"}
```
- 返回示例：
```json
{
  "code": "sh600519",
  "name": "贵州茅台",
  "price": 1335.0,
  "answer": "当前价 1335 元，市盈率……"
}
```

## 项目结构
```
agent_study/
├── main.py              # 盯盘助手后端（FastAPI 主程序）
├── .env                 # 密钥文件（不入库，需自建）
├── .gitignore           # 忽略 venv / 日志 / .env 等
├── requirements.txt     # 依赖清单
└── stock_crawler.py     # S1 验收项目：定时行情抓取脚本
```

## 技术要点（S2 知识点对应）
- FastAPI 路由：`@app.get` / `@app.post`、路径参数 `{codes}`、Pydantic 请求体。
- 调用大模型：OpenAI 兼容接口、`messages` 剧本、`stream=True` 流式输出。
- 异步路由：`async def` + `asyncio.gather` 并发；同步 I/O 用 `asyncio.to_thread` 托管。
- 密钥安全：`os.getenv` + `python-dotenv` + `.gitignore`。
- 本地运行：`uvicorn` 启动、`--reload` 开发热重载、`log_level="debug"` 排错。

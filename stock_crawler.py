"""
行情抓取脚本（S1 验收项目 · 完整版）
功能：定时拉取自选股实时行情 → 追加写入 CSV → 出错写日志不崩。
数据源：腾讯财经免费接口（requests 直连，无需 akshare 重依赖）。
依赖：requests、schedule（见 requirements.txt）
"""
import csv
import logging
import os
import time
from datetime import datetime

import requests
import schedule

# ---------- 配置区（改这里就行） ----------
WATCHLIST = ["600519", "000001", "300750"]   # 自选股 6 位代码：茅台 / 平安银行 / 宁德时代
SCHEDULE_AT = "15:30"                          # 每个交易日收盘后抓取（可改时间）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "quotes.csv")
LOG_FILE = os.path.join(BASE_DIR, "stock_crawler.log")

# ---------- 日志（S1 第7课：logging 比 print 好，可写文件留档） ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
)
logger = logging.getLogger(__name__)

# ---------- 抓取（S1 第6课：requests GET + raise_for_status + timeout） ----------
def add_prefix(code):
    """6 开头沪市加 sh，其余深市加 sz。"""
    return ("sh" if code.startswith("6") else "sz") + code

def fetch_quotes():
    """调用腾讯财经接口，返回 [[时间, 代码, 现价, 涨跌幅%], ...]。"""
    url = "https://qt.gtimg.cn/q=" + ",".join(add_prefix(c) for c in WATCHLIST)
    r = requests.get(url, timeout=10)
    r.raise_for_status()          # 非 2xx 主动抛异常（配合下面 except 接住）
    r.encoding = "gbk"            # 腾讯接口返回 GBK 编码，不设置会乱码
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for line in r.text.strip().split(";"):
        if "=" not in line:
            continue
        data = line.split("~")
        # 腾讯字段固定位置：2=代码 3=现价 32=涨跌幅(%)
        rows.append([now, data[2], data[3], data[32]])
    return rows

# ---------- 写 CSV（S1 第4课：with 自动关文件 / newline="" 防空行） ----------
def save_to_csv(rows):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["时间", "代码", "现价", "涨跌幅%"])   # 只在首次写表头
        writer.writerows(rows)
    logger.info(f"已写入 {len(rows)} 条行情到 {CSV_FILE}")

# ---------- 一次任务（S1 第7课：try/except 包住，出错记日志不崩） ----------
def job():
    try:
        logger.info("开始抓取行情")
        rows = fetch_quotes()       # 网络异常会在这里抛出
        if rows:
            save_to_csv(rows)
        else:
            logger.warning("本次未解析到任何行情，跳过写文件")
    except Exception as e:
        logger.error(f"抓取失败：{e}", exc_info=True)   # exc_info 把堆栈也写进日志，方便排查

# ---------- 定时（S1 第8课：schedule 靠 while 循环轮询触发） ----------
if __name__ == "__main__":
    job()                                          # 先立即跑一次（方便你测试）
    schedule.every().day.at(SCHEDULE_AT).do(job)   # 每天 SCHEDULE_AT 定时跑
    logger.info(f"已进入定时模式，每天 {SCHEDULE_AT} 抓取；按 Ctrl+C 退出")
    while True:
        schedule.run_pending()
        time.sleep(1)

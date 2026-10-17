import csv
import logging
import os
from datetime import datetime

import akshare as ak

WATCHLIST = ["600519", "000001", "300750"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
CSV_FILE = os.path.join(BASE_DIR, "quotes.csv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(
        os.path.join(BASE_DIR, "fetch.log"), encoding="utf-8")],
)


def add_prefix(code):
    return ("sh" if code.startswith("6") else "sz") + code


def fetch_quotes():
    df = ak.stock_zh_a_spot_em()               # 一次请求拉回全市场
    df = df[df["代码"].isin(WATCHLIST)]         # 按自选股清单筛选
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [[now, r["代码"], r["最新价"], r["涨跌幅"]]
            for _, r in df.iterrows()]


def save_to_csv(rows):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["时间", "代码", "现价", "涨跌幅%"])
        writer.writerows(rows)


if __name__ == "__main__":
    try:
        rows = fetch_quotes()
        save_to_csv(rows)
        logging.info(f"抓取成功，写入 {len(rows)} 条行情")
    except Exception as e:
        logging.error(f"本次抓取失败：{e}")

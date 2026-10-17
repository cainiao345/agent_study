import csv
import logging
import os
from datetime import datetime

import requests

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
    url = "https://qt.gtimg.cn/q=" + ",".join(add_prefix(c) for c in WATCHLIST)
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    r.encoding = "gbk"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for line in r.text.strip().split(";"):
        if "=" not in line:
            continue
        data = line.split("~")
        rows.append([now, data[2], data[3], data[32]])
    return rows


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

# 行情抓取脚本（S1 验收项目）

定时拉取自选股实时行情，追加保存到本地 CSV，出错写日志不中断，可定时自动运行。

## 功能
- 用 `requests` 直连腾讯财经免费行情接口（无需 akshare 重依赖）
- 数据**追加**写入 `quotes.csv`（时间、代码、现价、涨跌幅%）
- 失败写入 `stock_crawler.log` 日志，程序不崩溃
- `schedule` 定时执行（默认每个交易日 15:30 收盘后）

## 目录结构
- `stock_crawler.py` —— 主程序（抓取 + 写 CSV + 日志 + 定时）
- `fetch.py` / `fetch_once.py` —— 早期实验版本（可删除，仅供对照）
- `quotes.csv` —— 运行时生成的数据（已被 .gitignore 忽略）
- `requirements.txt` —— 依赖清单
- `.gitignore` —— 忽略 venv / 日志 / 缓存

## 使用方法
1. 创建并激活虚拟环境（推荐，隔离依赖）：
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 修改 `stock_crawler.py` 顶部的 `WATCHLIST` 配置你的自选股（6 位代码）。
4. 运行：
   ```bash
   python stock_crawler.py
   ```
   程序会**立即抓取一次**（方便测试），随后进入定时模式，每天 15:30 抓取；按 `Ctrl+C` 退出。

## 自选股配置
`WATCHLIST` 中 `6` 开头为沪市（自动加 `sh` 前缀），`0/3` 开头为深市（自动加 `sz` 前缀），脚本自动补全。

## CSV 格式
| 时间 | 代码 | 现价 | 涨跌幅% |
| --- | --- | --- | --- |
| 2026-10-17 15:30:01 | 600519 | 1500.00 | 2.35 |

## 定时部署（两种任选）
- **方式 A（脚本自带）**：直接运行 `python stock_crawler.py`，靠内部 `while True` 轮询；需保持窗口开着。
- **方式 B（生产推荐，Windows 任务计划）**：
  1. 打开 `taskschd.msc`，创建任务"每日行情抓取"。
  2. 触发器：每天 15:30。
  3. 操作：程序填 `venv\Scripts\pythonw.exe` 完整路径，参数 `stock_crawler.py`，"起始于"填项目目录。
  4. 勾选"不管用户是否登录都要运行"。
  （任务计划看不到终端，所以脚本用 `logging` 写文件日志排查。）

## 上传 GitHub
```bash
git add .
git commit -m "完成 S1 验收项目：行情抓取脚本"
git push -u origin main
```
（首次需先 `git remote add origin <你的仓库地址>`。）

## S1 知识点对应
requests（GET / 超时 / raise_for_status）· 异常处理 try/except · logging 写文件 · CSV 追加（newline / utf-8-sig）· schedule 定时 · Git 上传 · `if __name__ == "__main__"` 入口约定。

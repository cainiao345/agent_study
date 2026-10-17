# 行情抓取脚本

定时拉取自选股实时行情，追加保存到 CSV 文件。

## 功能
- requests 调用免费行情接口，支持批量查询
- 数据追加写入 quotes.csv（时间、代码、现价、涨跌幅）
- 失败写入 fetch.log 日志，程序不中断
- schedule 定时执行，默认每 30 分钟一次

## 使用方法
1. pip install -r requirements.txt
2. 修改 fetch.py 顶部的 WATCHLIST 配置自选股
3. python fetch.py

## 自选股配置
WATCHLIST 中 6 开头为沪市，0/3 开头为深市，脚本自动补全前缀。

## 定时部署（Windows 任务计划）
1. 打开 taskschd.msc，创建任务"每日行情抓取"
2. 触发器：每天 09:30
3. 操作：程序填 venv 的 pythonw.exe 完整路径，参数 fetch_once.py，起始于项目目录
4. 建议勾选"不管用户是否登录都要运行"


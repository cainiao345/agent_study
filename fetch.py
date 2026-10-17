import asyncio

async def 抓行情(代码):
    print(f"请求{代码}行情中...")
    await asyncio.sleep(1) 
    print(f"{代码}行情已获取")

async def main():
    await asyncio.gather(抓行情("AAPL"), 抓行情("GOOGL"), 抓行情("MSFT"))

asyncio.run(main())
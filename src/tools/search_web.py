import asyncio
from crawl4ai import AsyncWebCrawler

def crawl(url):
    async def run():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result
    return asyncio.run(run())


if __name__ == "__main__":
    url = "https://www.baidu.com"
    result = crawl(url)
    print(result.markdown)
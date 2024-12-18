import asyncio
import json

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

class ReadhubCrawler:
    def __init__(self):
        self.schema = {
            "name": "ReadHub News",
            "baseSelector": ".style_item__CkRvg",
            "fields": [
                {
                    "name": "title",
                    "selector": "a",
                    "type": "text",
                },
                {
                    "name": "content",
                    "selector": "p",
                    "type": "text",
                },
                {
                    "name": "link",
                    "selector": "a",
                    "type": "attribute",
                    "attribute": "href",
                }
            ],
        }

    async def extract_using_css_extractor(self):
        print("\n--- Crawling news from readhub.cn ---")

        # Create the extraction strategy
        extraction_strategy = JsonCssExtractionStrategy(self.schema, verbose=True)

        # Use the AsyncWebCrawler with the extraction strategy
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url="https://www.readhub.cn/daily",
                extraction_strategy=extraction_strategy,
                bypass_cache=True,
            )

            assert result.success, "Failed to crawl the page"

            # Parse the extracted content
            news = json.loads(result.extracted_content)
            for item in news:
                item['link'] = f"https://www.readhub.cn{item['link']}"
            print(f"Successfully extracted {len(news)} news")

        return news

    def get_news(self):
        return asyncio.run(self.extract_using_css_extractor())

service = ReadhubCrawler()
print(json.dumps(service.get_news(), indent=2, ensure_ascii=False))

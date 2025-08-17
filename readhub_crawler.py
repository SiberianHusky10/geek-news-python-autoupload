import asyncio
import json
import os
from typing import List

from crawl4ai import AsyncWebCrawler, LLMConfig, CrawlResult, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from dotenv import load_dotenv

load_dotenv()

class ReadhubCrawler:
    def __init__(self):
        self.schema = {
            "name": "ReadHub News Articles",
            "baseSelector": "div.style_item__CkRvg",
            "fields": [
                {
                    "name": "number",
                    "selector": "span.style_number__xAPEI",
                    "type": "text"
                },
                {
                    "name": "title",
                    "selector": "a.style_link__tCu2n",
                    "type": "text"
                },
                {
                    "name": "url",
                    "selector": "a.style_link__tCu2n",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "summary",
                    "selector": "div.style_summary__unpsP p.style_p__pUPPi",
                    "type": "text"
                },
                {
                    "name": "entity_link",
                    "selector": "a.style_link__FWtSE",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "entity_name",
                    "selector": "a.style_link__FWtSE",
                    "type": "text"
                }
            ]
        }


    async def extract_using_css_extractor(self):
        print("\n--- Crawling news from readhub.cn ---")

        # Create the extraction strategy
        extraction_strategy = JsonCssExtractionStrategy(self.schema, verbose=True)

        # Use the AsyncWebCrawler with the extraction strategy
        async with AsyncWebCrawler(verbose=True) as crawler:
            result: List[CrawlResult] = await crawler.arun(
                url="https://www.readhub.cn/daily",
                config=CrawlerRunConfig(
                    extraction_strategy=extraction_strategy)
            )

            for item in result:
                print(f"URL: {item.url}")
                print(f"Status: {item.success}")
                if item.success:
                   data = json.loads(item.extracted_content)
                   print(json.dumps(data, indent=2, ensure_ascii=False))
                   return data



    def get_news(self):
        return asyncio.run(self.extract_using_css_extractor())

    async def generate_schema(self):
        schema = JsonCssExtractionStrategy.generate_schema(
            html="""<div class="style_item__CkRvg style_fade__8u6eW"><article class="style_article__lAzaP"><div class="style_title__OBXz_"><span class="__className_4d59f0 style_number__xAPEI">01</span><a target="_blank" class="panda-trs_color_0.3s_ease hover:panda-td_underline hover:panda-tu-o_2px hover:panda-c_var(--text-primary-color) style_link__tCu2n" href="/topic/8lmXGKxBBzx">接近 DeepSeek 人士确认：DeepSeek-R2 在 8 月内并无发布计划</a></div><div class="style_pretty__21h8T style_summary__unpsP"><div class="style_richtext__7WXtl"><p class="style_p__pUPPi">市场再度传出<a style="--line-width:2px;--line-offset:-4px" target="_blank" class="style_link__FWtSE" href="/entity_topics?type=10&amp;uid=6d92808e73cc3ad3">深度求索（DeepSeek）</a>下一代大模型 DeepSeek-R2 的发布消息，预计时间窗口为 8 月 15 日至 30 日。</p></div></div></article></div>""",
            llm_config=LLMConfig(provider="deepseek/deepseek-chat",
                                 api_token=os.getenv("DEEPSEEK_API_KEY")),
            query="I have shares a sample of one news div with a title, content, link, and other metadata. Please generate a JSON schema for extracting news articles from ReadHub.",
        )

        print(json.dumps(schema, indent=2, ensure_ascii=False))

service = ReadhubCrawler()
# asyncio.run(service.generate_schema())
print(json.dumps(service.get_news(), indent=2, ensure_ascii=False))# print(json.dumps(service.get_news(), indent=2, ensure_ascii=False))


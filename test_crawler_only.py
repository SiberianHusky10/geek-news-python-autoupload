"""
单独测试爬虫功能
"""
from readhub_crawler import ReadhubCrawler
import json

def test_crawler():
    print("=== 🧪 单独测试爬虫功能 ===\n")

    crawler = ReadhubCrawler()

    # 测试爬取
    news_data = crawler.get_news()

    if news_data:
        print(f"\n✅ 测试成功!")
        print(f"📊 获取到 {len(news_data)} 条新闻")

        # 显示详细信息
        print(f"\n📰 新闻详情:")
        for i, item in enumerate(news_data[:3], 1):
            print(f"\n{i}. 标题: {item.get('title', '无标题')}")
            print(f"   内容长度: {len(item.get('content', ''))} 字符")
            print(f"   内容预览: {item.get('content', '无内容')[:100]}...")
            print(f"   链接: {item.get('link', '无链接')}")

        # 保存测试结果
        with open('test_crawler_result.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 测试结果已保存到 test_crawler_result.json")

        return True
    else:
        print(f"\n❌ 测试失败，未能获取到新闻数据")
        return False

if __name__ == "__main__":
    success = test_crawler()
    if success:
        print(f"\n🎉 爬虫测试通过，可以继续使用完整功能!")
    else:
        print(f"\n😞 爬虫测试失败，请检查网络连接或稍后重试")

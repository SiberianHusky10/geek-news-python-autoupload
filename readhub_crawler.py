import json
import requests
from bs4 import BeautifulSoup
import time

class ReadhubCrawler:
    """
    简化的ReadHub爬虫，只使用requests + BeautifulSoup方法
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def get_news(self):
        """
        获取ReadHub新闻数据
        """
        print("🚀 开始爬取readhub新闻...")

        try:
            # 添加重试机制
            for attempt in range(3):
                try:
                    response = requests.get(
                        'https://www.readhub.cn/daily',
                        headers=self.headers,
                        timeout=30,
                        verify=False  # 忽略SSL验证
                    )
                    response.raise_for_status()
                    print(f"✅ 第 {attempt + 1} 次请求成功")
                    break
                except requests.RequestException as e:
                    print(f"❌ 请求失败 (尝试 {attempt + 1}/3): {str(e)}")
                    if attempt < 2:
                        print("⏳ 等待5秒后重试...")
                        time.sleep(5)
                    else:
                        raise

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('.style_item__CkRvg')

            if not news_items:
                print("❌ 未找到新闻项目，可能页面结构已改变")
                return []

            print(f"📰 找到 {len(news_items)} 个新闻项目")

            news = []
            for i, item in enumerate(news_items, 1):
                try:
                    title_elem = item.select_one('a')
                    content_elem = item.select_one('p')

                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        content = content_elem.get_text(strip=True) if content_elem else ""
                        link = title_elem.get('href', '')

                        if link and not link.startswith('http'):
                            link = f"https://www.readhub.cn{link}"

                        if title:  # 只添加有标题的项目
                            news.append({
                                'title': title,
                                'content': content,
                                'link': link
                            })
                            print(f"✅ 解析第 {i} 条: {title[:30]}...")
                        else:
                            print(f"⚠️ 第 {i} 条新闻无标题，跳过")
                    else:
                        print(f"⚠️ 第 {i} 条新闻无链接元素，跳过")

                except Exception as e:
                    print(f"❌ 解析第 {i} 条新闻时出错: {str(e)}")
                    continue

            print(f"🎉 成功解析 {len(news)} 条新闻")
            return news

        except Exception as e:
            print(f"❌ 爬取过程发生错误: {str(e)}")
            return []

    def test_connection(self):
        """
        测试网站连接
        """
        print("🔍 测试readhub.cn连接...")

        try:
            response = requests.get(
                'https://www.readhub.cn/daily',
                headers=self.headers,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                print("✅ 网站连接正常")
                print(f"📊 页面大小: {len(response.text)} 字符")

                # 检查是否包含新闻元素
                if '.style_item__CkRvg' in response.text:
                    print("✅ 页面包含新闻元素")
                else:
                    print("⚠️ 页面可能不包含新闻元素")

                return True
            else:
                print(f"❌ 网站返回状态码: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 连接测试失败: {str(e)}")
            return False

# 测试代码
if __name__ == "__main__":
    print("=== 简化版ReadHub爬虫测试 ===\n")

    crawler = ReadhubCrawler()

    # 先测试连接
    if crawler.test_connection():
        print("\n" + "="*50)

        # 开始爬取
        news_data = crawler.get_news()

        if news_data:
            print(f"\n📊 爬取结果统计:")
            print(f"   - 成功获取: {len(news_data)} 条新闻")
            print(f"   - 平均标题长度: {sum(len(item.get('title', '')) for item in news_data) / len(news_data):.1f} 字符")
            print(f"   - 平均内容长度: {sum(len(item.get('content', '')) for item in news_data) / len(news_data):.1f} 字符")

            # 显示前3条新闻
            print(f"\n📰 前3条新闻预览:")
            for i, item in enumerate(news_data[:3], 1):
                print(f"\n{i}. {item.get('title', '无标题')}")
                print(f"   内容: {item.get('content', '无内容')[:80]}...")
                print(f"   链接: {item.get('link', '无链接')}")

            # 保存结果
            with open('simple_crawler_result.json', 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 数据已保存到 simple_crawler_result.json")

        else:
            print("\n😞 未能获取到任何新闻数据")
    else:
        print("\n❌ 网站连接失败，无法继续爬取")

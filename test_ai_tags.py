from ai_tag_generator import AITagGenerator
import json

def test_ai_tag_generation():
    """
    测试AI标签生成功能
    """
    generator = AITagGenerator()

    # 测试数据
    test_articles = [
        {
            "title": "OpenAI发布GPT-4新版本，性能大幅提升",
            "content": "OpenAI今天宣布发布GPT-4的最新版本，该版本在自然语言处理、代码生成和推理能力方面都有显著提升。新版本采用了更先进的训练技术，能够更好地理解上下文和生成更准确的回答。"
        },
        {
            "title": "特斯拉自动驾驶技术获得重大突破",
            "content": "特斯拉公司宣布其自动驾驶技术在最新测试中取得重大突破，FSD系统的安全性和可靠性得到显著提升。该技术将在未来几个月内推广到更多车型。"
        },
        {
            "title": "苹果发布新款MacBook Pro，搭载M3芯片",
            "content": "苹果公司今日发布了搭载全新M3芯片的MacBook Pro系列产品。新芯片采用3纳米工艺制造，性能相比上一代提升30%，同时功耗降低20%。"
        }
    ]

    print("=== AI标签生成测试 ===\n")

    for i, article in enumerate(test_articles, 1):
        print(f"测试文章 {i}:")
        print(f"标题: {article['title']}")
        print(f"内容: {article['content'][:100]}...")

        tags = generator.generate_tags(article['title'], article['content'])
        print(f"生成的标签: {tags}")
        print(f"标签长度: {len(tags)} 字符")
        print("-" * 50)

if __name__ == "__main__":
    test_ai_tag_generation()

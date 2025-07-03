import os
from openai import OpenAI

class AITagGenerator:
    def __init__(self):
        # 检查可用的API配置
        self.clients = self._setup_clients()

    def _setup_clients(self):
        """
        设置多个AI客户端作为备选方案
        """
        clients = []

        # 1. 阿里云DashScope (通义千问)
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        if dashscope_key:
            try:
                client = OpenAI(
                    api_key=dashscope_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                clients.append({
                    'name': 'DashScope',
                    'client': client,
                    'model': 'qwen-turbo',  # 使用DashScope支持的模型
                    'max_tokens': 100
                })
                print("✓ DashScope客户端配置成功")
            except Exception as e:
                print(f"✗ DashScope客户端配置失败: {e}")

        # 2. xAI (Grok)
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            try:
                client = OpenAI(
                    api_key=xai_key,
                    base_url="https://api.x.ai/v1"
                )
                clients.append({
                    'name': 'xAI',
                    'client': client,
                    'model': 'grok-beta',  # 使用正确的grok模型名称
                    'max_tokens': 100
                })
                print("✓ xAI客户端配置成功")
            except Exception as e:
                print(f"✗ xAI客户端配置失败: {e}")

        # 3. OpenAI (如果有API key)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                client = OpenAI(api_key=openai_key)
                clients.append({
                    'name': 'OpenAI',
                    'client': client,
                    'model': 'gpt-3.5-turbo',
                    'max_tokens': 100
                })
                print("✓ OpenAI客户端配置成功")
            except Exception as e:
                print(f"✗ OpenAI客户端配置失败: {e}")

        if not clients:
            print("⚠️ 没有可用的AI客户端，将使用备用标签生成方法")

        return clients

    def generate_tags(self, title, content):
        """
        根据文章标题和内容生成标签
        返回少于100字符的标签字符串
        """
        # 构建提示词
        prompt = f"""
请根据以下文章的标题和内容，生成3-5个相关的标签。
要求：
1. 标签用中文
2. 标签之间用逗号分隔
3. 总长度不超过90个字符
4. 标签要准确反映文章的主要内容和主题
5. 优先选择技术、行业、公司名称等关键词作为标签

文章标题：{title}

文章内容：{content[:500]}...

请直接返回标签，不要其他解释：
"""

        # 尝试使用每个可用的客户端
        for client_config in self.clients:
            try:
                print(f"尝试使用 {client_config['name']} 生成标签...")

                response = client_config['client'].chat.completions.create(
                    model=client_config['model'],
                    messages=[
                        {"role": "system", "content": "你是一个专业的内容标签生成助手，擅长为科技新闻生成准确的标签。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=client_config['max_tokens'],
                    temperature=0.3
                )

                tags = response.choices[0].message.content.strip()

                # 确保标签长度不超过90字符
                if len(tags) > 90:
                    tags = tags[:87] + "..."

                print(f"✓ {client_config['name']} 成功生成标签: {tags}")
                return tags

            except Exception as e:
                print(f"✗ {client_config['name']} 生成失败: {str(e)}")
                continue

        # 如果所有AI服务都失败，使用备用方法
        print("所有AI服务都失败，使用备用标签生成方法")
        return self._generate_fallback_tags(title)

    def _generate_fallback_tags(self, title):
        """
        当AI生成失败时的备用标签生成方法
        """
        print("使用备用标签生成方法...")

        # 扩展的关键词库
        tech_keywords = {
            'AI': ['AI', '人工智能', 'GPT', 'ChatGPT', 'OpenAI', '机器学习', '深度学习'],
            '区块链': ['区块链', '比特币', '以太坊', 'Web3', 'NFT', '加密货币'],
            '芯片': ['芯片', '半导体', '处理器', 'CPU', 'GPU', 'M1', 'M2', 'M3'],
            '汽车': ['特斯拉', '自动驾驶', '电动车', '新能源', '汽车'],
            '科技公司': ['苹果', '谷歌', '微软', '亚马逊', 'Meta', '字节跳动', '腾讯', '阿里巴巴'],
            '技术': ['云计算', '大数据', '物联网', 'VR', 'AR', '5G', '6G', '量子计算'],
            '互联网': ['互联网', '社交媒体', '电商', '直播', '短视频']
        }

        found_tags = []
        title_lower = title.lower()

        # 检查标题中包含的关键词
        for category, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword.lower() in title_lower or keyword in title:
                    found_tags.append(category)
                    break

        # 如果没找到特定关键词，添加通用标签
        if not found_tags:
            found_tags = ['科技', '新闻']

        # 限制标签数量
        result_tags = found_tags[:3]
        result = ','.join(result_tags)

        print(f"备用方法生成的标签: {result}")
        return result

    def test_connection(self):
        """
        测试AI服务连接
        """
        print("=== 测试AI服务连接 ===")

        test_title = "测试标题"
        test_content = "这是一个测试内容"

        for client_config in self.clients:
            try:
                print(f"测试 {client_config['name']}...")

                response = client_config['client'].chat.completions.create(
                    model=client_config['model'],
                    messages=[
                        {"role": "user", "content": "请回复'连接成功'"}
                    ],
                    max_tokens=10
                )

                result = response.choices[0].message.content.strip()
                print(f"✓ {client_config['name']} 连接成功: {result}")

            except Exception as e:
                print(f"✗ {client_config['name']} 连接失败: {str(e)}")

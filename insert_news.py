from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, func
from sqlalchemy.orm import sessionmaker, declarative_base
from readhub_crawler import ReadhubCrawler
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取数据库连接 URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 数据库连接设置
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    title = Column(String(30), nullable=False, comment='文章标题')
    content = Column(String(10000), nullable=False, comment='文章内容')
    cover_img = Column(String(128), nullable=False, comment='文章封面')
    state = Column(Enum('已发布', '草稿'), default='草稿', comment='文章状态: 只能是[已发布] 或者 [草稿]')
    category_id = Column(Integer, comment='文章分类ID')
    create_user = Column(Integer, nullable=False, comment='创建人ID')
    create_time = Column(DateTime, nullable=False, comment='创建时间')
    update_time = Column(DateTime, nullable=False, comment='修改时间')


def insert_article(article_data):
    session = Session()
    try:
        # 确保 article_data 是一个列表
        if isinstance(article_data, str):
            article_data = json.loads(article_data)
            print("working")

        if not isinstance(article_data, list):
            article_data = [article_data]
            print("working")

        # 获取 article 表中的数据个数
        article_count = session.query(func.count(Article.id)).scalar()

        id_counter = article_count + 1
        print(f"article 表中的数据个数加一为: {id_counter}")

        #定义一个变量记录成功循环的次数
        success_count = 0
        for item in article_data:
            # 检查数据库中是否已经存在相同标题的文章
            existing_article = session.query(Article).filter_by(title=item.get('title', '')[:30]).first()
            if existing_article:
                print(f"文章 '{item.get('title', '')[:30]}' 已存在，跳过插入。")
                continue

            current_time = datetime.utcnow()
            article = Article(
                id=id_counter,
                title=item.get('title', '')[:30],  # 限制标题长度为30
                content=item.get('content', '')[:10000],  # 限制内容长度为10000
                cover_img=item.get('link', '')[:128],  # 限制封面图片URL长度为128
                state=item.get('state', '草稿'),
                category_id=item.get('category_id', 3),
                create_user=item.get('create_user', 4),  # 假设默认用户ID为4
                create_time=current_time,
                update_time=current_time
            )
            session.add(article)
            print(article.__dict__)
            id_counter += 1
            success_count += 1
        session.commit()
        print(f"成功将 {success_count} 条文章插入数据库。")
    except Exception as e:
        session.rollback()
        print(f"发生错误：{str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    crawler = ReadhubCrawler()
    article_data = crawler.get_news()

    # 如果 article_data 是字符串，尝试解析它
    if isinstance(article_data, str):
        try:
            article_data = json.loads(article_data)
        except json.JSONDecodeError:
            print("无法解析文章数据，可能不是有效的 JSON 格式")
            article_data = []

    # 处理爬取的数据，确保符合新的表结构
    for item in article_data:
        item['state'] = '草稿'  # 默认状态为草稿
        item['create_user'] = 4  # 假设默认用户ID为1
        # 如果爬虫没有提供 category_id，可以设置一个默认值或留空

    insert_article(article_data)



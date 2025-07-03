from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, func
from sqlalchemy.orm import sessionmaker, declarative_base
from readhub_crawler import ReadhubCrawler
from ai_tag_generator import AITagGenerator
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import time

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    title = Column(String(30), nullable=False, comment='文章标题')
    content = Column(String(10000), nullable=False, comment='文章内容')
    cover_img = Column(String(128), nullable=False, comment='文章封面')
    state = Column(Enum('已发布', '草稿'), default='草稿', comment='文章状态')
    category_id = Column(Integer, comment='文章分类ID')
    create_user = Column(Integer, nullable=False, comment='创建人ID')
    create_time = Column(DateTime, nullable=False, comment='创建时间')
    update_time = Column(DateTime, nullable=False, comment='修改时间')
    tags = Column(String(100), comment='标签')

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)

def ensure_dependencies():
    """
    确保数据库中有必要的依赖数据
    """
    session = Session()

    try:
        # 检查并创建分类
        category_count = session.query(func.count(Category.id)).scalar()
        if category_count == 0:
            print("📋 创建默认分类...")
            categories = [
                Category(id=1, name='科技新闻'),
                Category(id=2, name='AI资讯'),
                Category(id=3, name='行业动态'),
                Category(id=4, name='产品发布'),
                Category(id=5, name='公司新闻')
            ]
            for cat in categories:
                session.add(cat)
            session.commit()
            print("✅ 默认分类创建完成")

        # 检查并创建用户
        user_count = session.query(func.count(User.id)).scalar()
        if user_count == 0:
            print("👤 创建默认用户...")
            users = [
                User(id=1, username='admin'),
                User(id=2, username='editor'),
                User(id=3, username='crawler'),
                User(id=4, username='system')
            ]
            for user in users:
                session.add(user)
            session.commit()
            print("✅ 默认用户创建完成")

        # 获取有效的ID
        first_category = session.query(Category).first()
        first_user = session.query(User).first()

        return first_category.id if first_category else 1, first_user.id if first_user else 1

    except Exception as e:
        session.rollback()
        print(f"❌ 创建依赖数据时出错: {str(e)}")
        return 1, 1
    finally:
        session.close()

def insert_articles_with_ai_tags(article_data):
    """
    插入文章数据到数据库，包含AI生成的标签
    """
    if not article_data:
        print("❌ 没有文章数据可插入")
        return 0

    # 确保依赖数据存在
    category_id, user_id = ensure_dependencies()

    session = Session()
    ai_generator = AITagGenerator()

    try:
        # 获取当前文章数量
        article_count = session.query(func.count(Article.id)).scalar()
        id_counter = article_count + 1
        print(f"📊 当前数据库中有 {article_count} 条文章")
        print(f"📊 使用分类ID: {category_id}, 用户ID: {user_id}")

        success_count = 0
        skipped_count = 0

        for i, item in enumerate(article_data, 1):
            title = item.get('title', '').strip()
            content = item.get('content', '').strip()

            if not title:
                print(f"⚠️ 第 {i} 条新闻无标题，跳过")
                continue

            # 检查是否已存在
            existing_article = session.query(Article).filter_by(title=title[:30]).first()
            if existing_article:
                print(f"⚠️ 第 {i} 条新闻已存在: '{title[:30]}'")
                skipped_count += 1
                continue

            # 生成AI标签
            print(f"🤖 第 {i} 条: 为 '{title[:30]}...' 生成AI标签")
            ai_tags = ai_generator.generate_tags(title, content)

            # 创建文章记录
            current_time = datetime.utcnow()
            article = Article(
                id=id_counter,
                title=title[:30],
                content=content[:10000],
                cover_img=item.get('link', '')[:128],
                state='草稿',
                category_id=category_id,
                create_user=user_id,
                create_time=current_time,
                update_time=current_time,
                tags=ai_tags
            )

            session.add(article)
            print(f"✅ 准备插入: ID={id_counter}, 标签='{ai_tags}'")

            id_counter += 1
            success_count += 1

            # 避免API限制
            time.sleep(0.5)

        # 提交到数据库
        if success_count > 0:
            session.commit()
            print(f"\n🎉 成功插入 {success_count} 条文章到数据库!")
        else:
            print(f"\n⚠️ 没有新文章需要插入")

        if skipped_count > 0:
            print(f"📝 跳过了 {skipped_count} 条重复文章")

        return success_count

    except Exception as e:
        session.rollback()
        print(f"❌ 插入数据库时发生错误: {str(e)}")
        return 0
    finally:
        session.close()

def main():
    """
    主程序入口
    """
    print("=" * 60)
    print("🚀 优化版ReadHub新闻爬取和AI标签生成系统")
    print("=" * 60)

    # 步骤1: 爬取新闻
    print("\n📰 步骤1: 爬取新闻数据")
    crawler = ReadhubCrawler()

    # 先测试连接
    if not crawler.test_connection():
        print("❌ 网站连接失败，程序退出")
        return

    # 开始爬取
    article_data = crawler.get_news()

    if not article_data:
        print("❌ 爬取失败，程序退出")
        return

    # 显示爬取统计
    print(f"\n📊 爬取统计:")
    print(f"   - 总共获取: {len(article_data)} 条新闻")
    print(f"   - 平均标题长度: {sum(len(item.get('title', '')) for item in article_data) / len(article_data):.1f} 字符")
    print(f"   - 平均内容长度: {sum(len(item.get('content', '')) for item in article_data) / len(article_data):.1f} 字符")

    # 步骤2: 生成AI标签并插入数据库
    print(f"\n🤖 步骤2: 生成AI标签并插入数据库")
    success_count = insert_articles_with_ai_tags(article_data)

    # 最终统计
    print(f"\n" + "=" * 60)
    print(f"✅ 程序执行完成!")
    print(f"📊 最终统计:")
    print(f"   - 爬取新闻: {len(article_data)} 条")
    print(f"   - 成功插入: {success_count} 条")
    print(f"   - 跳过重复: {len(article_data) - success_count} 条")
    print("=" * 60)

if __name__ == "__main__":
    main()




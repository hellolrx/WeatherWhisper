# ingest_pinecone.py (最终版 - 直接读取Excel)
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
import time
from pathlib import Path

def ingest_data():
    """
    读取Excel知识库 (.xlsx)，生成向量，并将其上传到Pinecone。
    """
    # --- 初始化 ---
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    INDEX_NAME = "fashion-advice"

    if not all([PINECONE_API_KEY, PINECONE_ENVIRONMENT]):
        print("错误: Pinecone API Key或Environment未在.env文件中设置。")
        return

    # 1. 初始化Pinecone
    print("正在初始化Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"索引 '{INDEX_NAME}' 不存在。请在Pinecone官网手动创建。")
        return
    
    index = pc.Index(INDEX_NAME)
    print("Pinecone索引准备就绪。")

    # 2. 加载Embedding模型
    print("正在加载Embedding模型 (首次运行需要下载)...")
    model = SentenceTransformer('BAAI/bge-base-zh-v1.5')
    print("模型加载完毕。")

    # 3. 读取知识库 (*** 修改处：从读取CSV改为读取Excel ***)
    excel_path = Path(__file__).resolve().parent / 'knowledge_base.xlsx'
    print(f"尝试读取知识库文件: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path)
    except FileNotFoundError:
        print(f"错误: 文件未找到 at path: {excel_path}")
        return
    except Exception as e:
        print(f"读取Excel文件时发生错误: {e}")
        return

    df.dropna(inplace=True)
    print("Excel文件读取成功。")

    # 4. 生成向量并准备上传数据
    print("正在生成向量...")
    vectors_to_upsert = []
    for _, row in df.iterrows():
        try:
            embedding = model.encode(str(row['suggestion']), normalize_embeddings=True).tolist()
            vector_data = {
                "id": str(row['id']),
                "values": embedding,
                "metadata": {
                    "text": str(row['suggestion']),
                    "category": str(row['category'])
                }
            }
            vectors_to_upsert.append(vector_data)
        except Exception as e:
            print(f"处理行 ID={row.get('id', 'N/A')} 时出错: {e}")
            continue

    # 5. 分批上传到Pinecone
    if not vectors_to_upsert:
        print("没有可上传的数据。请检查Excel文件内容。")
        return

    print(f"准备上传 {len(vectors_to_upsert)} 条向量到Pinecone...")
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"成功上传批次 {i // batch_size + 1}")
        except Exception as e:
            print(f"上传批次 {i // batch_size + 1} 时出错: {e}")

    print("数据入库完成！")
    index_stats = index.describe_index_stats()
    print("Pinecone索引状态:", index_stats)

if __name__ == '__main__':
    ingest_data()
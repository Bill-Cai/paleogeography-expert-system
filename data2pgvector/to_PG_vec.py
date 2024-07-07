import numpy as np
from db.PostgresqlPool import pg_pool
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd
import re
from dateutil.parser import parse
import nltk

try:
    # 尝试加载分词器
    nltk.data.find('tokenizers/punkt')
except LookupError:
    # 如果未找到，使用NLTK的下载器下载并安装"punkt"数据文件
    nltk.download('punkt')

ABSTRACT = "abstract"


# clean embeddings
def clean_embed_vec(text: str):
    # remove line break
    text = re.sub(r'\n', '', text)
    # remove leading and trailing white spaces
    text = text.strip()
    # remove extra spaces
    text = re.sub('\s+', ' ', text)
    # remove strange characters in unicode
    text = text.encode("ascii", "ignore").decode()
    return text


def paragraph_seg(abstract: str, row, conn, cursor):
    cnt = 0
    # 在这里处理非NaN的"abstract"列值
    if '\n' in abstract:
        paragraphs = abstract.split('\n')
    else:
        paragraphs = [abstract]
    for index, paragraph in enumerate(paragraphs):
        if len(paragraph) > 0:
            # 在这里处理非空的段落
            vector = model.encode(clean_embed_vec(abstract))
            sql = "INSERT INTO sedimentology_paper_paragraph (doi, journal, title, authors, time, content_type, content, content_vec) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                row['doi'], row['journal'], row['title'], row['authors'], parse(row['time']), ABSTRACT, paragraph,
                vector))
            cnt += 1
    conn.commit()
    return cnt


def sentence_seg(abstract: str, row, conn, cursor):
    cnt = 0
    sent_tokenize_list = nltk.tokenize.sent_tokenize(abstract)
    for sent in sent_tokenize_list:
        if len(sent) > 0:
            vector = np.array(model.encode(clean_embed_vec(sent)))
            sql = "INSERT INTO sedimentology_paper_sentence (doi, journal, title, authors, time, content_type, content, content_vec) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                row['doi'], row['journal'], row['title'], row['authors'], parse(row['time']), ABSTRACT, sent, vector))
            cnt += 1
    conn.commit()
    return cnt


if __name__ == '__main__':

    # connect to Milvus server
    conn = pg_pool.get_connection()
    register_vector(conn)
    cursor = conn.cursor()

    # Load model
    # emb_dim = 384
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    total_inserted = 0

    # Load data
    data = pd.read_csv("Since2000.csv")
    for index, row in tqdm(data.iterrows(), total=len(data), desc="Processing rows"):
        abstract = row['abstract']
        if pd.notna(abstract):
            cnt = paragraph_seg(abstract, row, conn, cursor)
            cnt = sentence_seg(abstract, row, conn, cursor)
            total_inserted += cnt

    print(f"{total_inserted} records have been inserted. Done!")

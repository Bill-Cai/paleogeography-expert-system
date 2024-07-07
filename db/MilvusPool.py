from pymilvus import connections
from pymilvus import Collection
from typing import List
from sentence_transformers import SentenceTransformer

# todo get connection from config
# connections.connect(alias="dev", host="8.218.165.177", port="19530", user="root", password="Zju_gis_milvus")
# collection = Collection(name="paleo_paper2", using="dev")
# collection = Collection(name="paleo_paper_abstract_384d", using="dev")
# collection = Collection(name="paleo_paper_sentence", using="dev")


class Sentence:
    def __init__(self, doi, discipline, title, author, date, content_type, content):
        self.doi = doi
        self.discipline = discipline
        self.title = title
        self.author = author
        self.date = date
        self.content_type = content_type
        self.content = content

    def __str__(self):
        return f"DOI: {self.doi}\n" \
               f"Discipline: {self.discipline}\n" \
               f"Title: {self.title}\n" \
               f"Author: {self.author}\n" \
               f"Date: {self.date}\n" \
               f"Content Type: {self.content_type}\n" \
               f"Content: {self.content}\n"

    def to_ref(self):
        title = self.title.replace("_", " ")
        return f"Title: {title}; DOI: {self.doi}; Content: {self.content}"

    def to_dict(self):
        return {
            "doi": self.doi,
            "discipline": self.discipline,
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "content_type": self.content_type,
            "content": self.content
        }


# def search_vec(sentences: List, metric_type="L2", limit=5, expr=None) -> List:
#     model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#     embeddings = model.encode(sentences)
#     res = collection.search(
#         data=embeddings.tolist(),
#         anns_field="embed_vec",
#         param={"metric_type": metric_type},
#         limit=limit,
#         expr=expr,
#         # output_fields=["doi", "discipline", "title", "author", "date", "content_type", "content"]
#         output_fields=["doi", "journal", "title", "author", "date", "content_type", "content"]
#     )
#
#     related_sentences = []
#
#     for item in res:
#         sentence_list = []
#         for i in item:
#             dict = i.entity._row_data
#             entity = Sentence(
#                 dict['doi'],
#                 dict['journal'],
#                 dict['title'],
#                 dict['author'],
#                 dict['date'],
#                 dict['content_type'],
#                 dict['content']
#             )
#             sentence_list.append(entity)
#         related_sentences.append(sentence_list)
#
#     return related_sentences
import logging

import psycopg2
from psycopg2 import pool
from config import cfg
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from pgvector.psycopg2 import register_vector

from db.MilvusPool import Sentence


class PostgresqlPool:
    __instance = None

    @staticmethod
    def get_instance():
        """Static method to get the singleton object"""
        if PostgresqlPool.__instance is None:
            PostgresqlPool()
        return PostgresqlPool.__instance

    def __init__(self):
        """Instantiation method"""
        if PostgresqlPool.__instance is not None:
            raise Exception("This is a singleton class, please use PostgresqlPool.get_instance() to get the object")
        else:
            PostgresqlPool.__instance = self
            try:
                # Set the connection pool parameters
                self.minconn = 1
                self.maxconn = 32
                self.conn_pool = psycopg2.pool.SimpleConnectionPool(self.minconn, self.maxconn,
                                                                    user=cfg.pgsql_user,
                                                                    password=cfg.pgsql_password,
                                                                    host=cfg.pgsql_host,
                                                                    port=cfg.pgsql_port,
                                                                    database=cfg.pgsql_database)
            except Exception as e:
                print("Connection pool creation failed: ", e)
                raise

    def get_connection(self):
        """Get a connection from the connection pool"""
        try:
            conn = self.conn_pool.getconn()
            register_vector(conn)
            return conn
        except Exception as e:
            print("Failed to get connection: ", e)
            raise

    def put_connection(self, conn):
        """Return the connection to the connection pool"""
        self.conn_pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in the connection pool"""
        self.conn_pool.closeall()


def search_vec_pg(conn, sentences: str, table_name, limit=5, metric_type="L2",
               model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'), expr=None) -> List:
    """Similarity search"""
    metric_dict = {"L2": "<->", "IP": "<#>", "cosine": "<=>"}  # metric_type: operator
    embeddings = np.array(model.encode(sentences))
    sql = f"SELECT * FROM {table_name} ORDER BY content_vec {metric_dict[metric_type]} %s LIMIT {limit}"
    cursor = conn.cursor()
    # must code like this, or it will raise error: TypeError
    cursor.execute(sql, (embeddings,))
    res = cursor.fetchall()

    sentence_list = []
    for result in res:
        doi, content_type, content, title, author, date, journal, _ = result
        sentence = Sentence(doi, journal, title, author, date, content_type, content)
        sentence_list.append(sentence.to_dict())

    return sentence_list

try:
    pg_pool = PostgresqlPool.get_instance()
except Exception as e:
    logger = logging.getLogger(__name__)
    pg_pool = None
    logger.warning(f"Failed to create PostgresqlPool: {e}")
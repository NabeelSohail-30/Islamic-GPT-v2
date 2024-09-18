from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
# from langchain_pinecone import PineconeVectorStore
# from pinecone import Pinecone
import tiktoken
import os
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore


load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
INDEX_NAME = os.getenv('INDEX_NAME')
CHAT_MODEL_NAME = os.getenv('CHAT_MODEL_NAME')

model_name = CHAT_MODEL_NAME

embeddings = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large')

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

# es = Elasticsearch("https://172.16.28.205/:9200",
#                    basic_auth=("elastic", "GflxnCuMncZbaDUaLJgX"), verify_certs=False)

es = Elasticsearch("http://172.16.28.205:9200", verify_certs=False)

index_name = INDEX_NAME
vectorstore = ElasticsearchStore(
    index_name=index_name, embedding=embeddings, es_connection=es
)

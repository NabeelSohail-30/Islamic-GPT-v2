from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import tiktoken
from dotenv import load_dotenv
import os
import config
import logging
from openai import OpenAI


logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(message)s',
    encoding='utf-8'
)


def calculate_tokens(text):
    tokens = config.encoding.encode(text)
    return len(tokens)


def generate_prompt_with_content(query, contents, max_tokens=12000):
    prompt_template = f"""
    You are an Islamic assistant. Your role is to provide precise answers to the user's query based solely on the content provided below. You must not create or infer new information; use only the information provided.

    Instructions:
    - Carefully read and understand the user's query.
    - Respond using only the content given below.
    - If the answer to the query is directly found in the content, provide that exact answer without modification.
    - Ensure that all responses are in Urdu.
    - Avoid adding any additional context or information outside of the provided content.
    - Maintain a respectful and accurate tone that aligns with Islamic teachings.
    - Atleast provide the answer from the content against the query of about 200 to 500 words

    Query: {query}

    Content : {contents}
    """

    final_prompt = prompt_template
    logging.error(f"Final Prompt: {final_prompt}")
    return final_prompt


def search_documents(query, k=1):
    try:
        logging.info(f"Query: {query}")
        query = query

        search_query = {
            "size": k,
            "_source": ["paragraph", "questions"],
            "query": {
                "bool": {
                    "should": [],
                    "minimum_should_match": 1
                }
            }
        }

        if query:
            search_query["query"]["bool"]["should"].append({
                "match_phrase": {
                    "questions": {
                        "query": query,
                        "analyzer": "custom_urdu_stopwords_analyzer",
                        "boost": 4
                    }
                }
            })

        if query:
            search_query["query"]["bool"]["should"].append({
                "match_phrase": {
                    "questions": {
                        "query": query,
                        "boost": 3
                    }
                }
            })

        if query:
            search_query["query"]["bool"]["should"].append({
                "term": {
                    "questions.keyword": {
                        "value": query,
                        "boost": 2
                    }
                }
            })

        if query:
            search_query["query"]["bool"]["should"].append({
                "match": {
                    "questions": {
                        "query": query,
                        "operator": "and",
                        "analyzer": "custom_urdu_stopwords_analyzer",
                        "fuzziness": "AUTO",
                        "minimum_should_match": "100%",
                        "boost": 1.5
                    }
                }
            })

        if query:
            search_query["query"]["bool"]["should"].append({
                "match": {
                    "questions": {
                        "query": query,
                        "operator": "or",
                        "analyzer": "custom_urdu_stopwords_analyzer",
                        "fuzziness": "AUTO",
                        "minimum_should_match": "80%",
                        "boost": 1
                    }
                }
            })

        response = config.es.search(index=config.index_name, body=search_query)

        hits = response['hits']['hits']
        results = [hit["_source"].get("paragraph", "") for hit in hits]

        return results

    except Exception as e:
        return e.message


def get_response(query):
    contents = search_documents(query=query)

    logging.info(f"Contents: {contents}")

    if not contents:
        return "مجھے اس سوال کا جواب نہیں مل سکا، براہ کرم دوسرا سوال کریں"

    final_prompt = generate_prompt_with_content(query, contents)

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": ("You are an Islamic assistant. Answer the user's query based only on the provided content. "
                                "If the answer is not present, respond with 'I don't know.'")
                },
                {
                    "role": "user",
                    "content": final_prompt
                }
            ]
        )
        final_response = response.choices[0].message.content
        return final_response

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "مجھے اس سوال کا جواب نہیں مل سکا، براہ کرم دوسرا سوال کریں"


def generate_vector(text):
    return config.embeddings.embed_query(text)

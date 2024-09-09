from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import tiktoken
from dotenv import load_dotenv
import os
from openai import OpenAI
import config


def calculate_tokens(text):
    tokens = config.encoding.encode(text)
    return len(tokens)


def generate_prompt_with_content(query, contents, max_tokens=4096):
    # prompt_template = f"""
    # You are an Islamic assistant. You have to answer the user's query accurately from the given content as per the user query.
    # You are restricted to answer the query from the given content and cannot generate new content on your own.

    # - Understand the user query carefully and generate the answer as an Islamic scholar from DawateIslami based on the provided content.
    # - If the query is in Urdu, answer in Urdu only.
    # - If the query is in English, answer in Urdu only.
    # - If the query is in a different language, answer in Urdu only.
    # - If the query is a greeting, reply to the greeting accordingly as an Islamic Scholar with Hadith.
    # - If the answer to the user query is not in the given content you have to answer i don't know, you are strictly restricted to answer the query from the given content and cannot generate from your own.
    # - All answers should be from Bahar-e-Shariat Book.

    # Query: {query} (Answer from the given Content i.e Bahar-e-Shariat Volume 01 only !!!!)
    # """

    prompt_template = f"""
    You are an Islamic assistant. Answer the user's query based only on the provided content. You must not generate new information and must only use the content given below.

    Instructions:
    - Understand the user's query and provide an answer *only* from the provided content.
    - Always answer in Urdu Language.
    - If the *exact answer* to the query is present in the provided content, respond with that specific answer *without adding or inferring any information*.
    - If the answer is not present in the provided content or is unclear, respond with "I don't know."

    Query: {query}

    Answer from the following content only (Bahar-e-Shariat Volume 01):
    """

    content_tokens = 0
    included_contents = []

    for i, content in enumerate(contents):
        temp_prompt = prompt_template + f"\nContent {i + 1}:\n{content}\n"
        current_tokens = calculate_tokens(temp_prompt)
        if current_tokens > max_tokens:
            break
        content_tokens = current_tokens
        included_contents.append(f"Content {i + 1}:\n{content}")

    final_prompt = prompt_template + "\n".join(included_contents)
    return final_prompt, content_tokens


def similarity_search(query, k=5):
    query_vector = config.embeddings.embed_query(query)

    search_query = {
        "size": k,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    response = config.es.search(index=config.index_name, body=search_query)
    hits = response['hits']['hits']

    contents = [hit["_source"]["chunk_text"] for hit in hits]
    return contents


def get_response(query):
    results = similarity_search(query=query, k=5)
    # contents = [result.page_content for result in results]

    final_prompt, token_count = generate_prompt_with_content(query, results)

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": ("You are an Islamic assistant. You must answer the user's query based solely on the provided content. "
                            "You are restricted to using only this content. If the answer is not present in the content, respond with 'I don't know.'")
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ]
    )

    final_response = response.choices[0].message.content
    return final_response

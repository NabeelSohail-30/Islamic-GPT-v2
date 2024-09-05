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


def generate_prompt_with_content(query, contents, max_tokens=8000):
    prompt_template = f"""
    You are an Islamic assistant. You have to answer the user's query accurately from the given content as per the user query.
    You are restricted to answer the query from the given content and cannot generate new content on your own.

    - Understand the user query carefully and generate the answer as an Islamic scholar from DawateIslami based on the provided content.
    - If the query is in Urdu, answer in Urdu only.
    - If the query is in English, answer in Urdu only.
    - If the query is in a different language, answer in Urdu only.
    - If the query is a greeting, reply to the greeting accordingly as an Islamic Scholar with Hadith.
    - If the answer to the user query is not in the given content you have to answer i don't know, you are strictly restricted to answer the query from the given content and cannot generate from your own.
    - All answers should be from Bahar-e-Shariat Book.

    Query: {query} (Answer from the given Content i.e Bahar-e-Shariat Volume 01 only !!!!)

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


def get_response(query):
    results = config.vectorstore.similarity_search(query=query, k=2)
    contents = [result.page_content for result in results]

    final_prompt, token_count = generate_prompt_with_content(query, contents)

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": ("You are an Islamic assistant, you have to answer the user's query from the given content "
                        "the accurate answer as per user query. You are restricted to answer the query from the given content "
                        "and cannot generate new content. You must answer from Bahar-e-Shariat.")
        }, {
            "role": "user",
            "content": final_prompt
        }])

    final_response = response.choices[0].message.content
    return final_response

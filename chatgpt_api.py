from openai import OpenAI
from utils.rag import (
    tourism_scrape_article,
    gourmet_scrape_article,
    faq_scrape_article,
    scrape_article,
    chunk_text,
    vectorize_text,
    find_most_similar,
    ask_question,
)
import boto3
import os
import json


def get_chatgpt_response(api_key, model, temperature, system_content, user_message):
    OPENAI_API_KEY = api_key
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def get_chatgpt_response_rag(
    user_message,
    urls,
    model,
    message_template,
    status,
    data=None,
    text_chunks=None,
    vectors=None,
):
    # s3_client = boto3.client('s3')
    # bucket_name = os.environ["BUCKET_NAME"]

    chunk_size = 300
    overlap = 30
    if data is None:
        if status == "gourmet":
            article_text = gourmet_scrape_article(urls)
        elif status == "tourism":
            article_text = tourism_scrape_article(urls)
        elif status == "faq":
            article_text = faq_scrape_article(urls)
        else:
            article_text = scrape_article(urls)
    else:
        article_text = data

    ### scraping_text_data_to_s3
    # file_name = f"{status}_data.txt"
    # s3_client.put_object(
    #     Bucket=bucket_name,
    #     Key=file_name,
    #     Body=article_text,
    #     ContentType='text/plain'
    # )

    if text_chunks is None:
        text_chunks = chunk_text(article_text, chunk_size, overlap)

    ### text_chunk_json_data_to_s3
    # text_chunks_json = json.dumps(text_chunks, ensure_ascii=False, indent=2)
    # file_name = f"{status}_text_chunks.json"
    # s3_client.put_object(
    #     Bucket=bucket_name,
    #     Key=file_name,
    #     Body=text_chunks_json,
    #     ContentType='application/json'
    # )
    if vectors is None:
        vectors = [vectorize_text(doc) for doc in text_chunks]

    ### vectors_json_data_to_s3
    # vectors_json = json.dumps(vectors)
    # s3_client = boto3.client('s3')
    # bucket_name = os.environ["BUCKET_NAME"]
    # file_name = f"{status}_vectors.json"
    # s3_client.put_object(
    #     Bucket=bucket_name,
    #     Key=file_name,
    #     Body=vectors_json,
    #     ContentType='application/json'
    # )

    question = user_message
    question_vector = vectorize_text(question)
    similar_document = find_most_similar(question_vector, vectors, text_chunks)
    answer = ask_question(question, similar_document, model, message_template)
    return answer

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import boto3
import zipfile
import sys
import numpy as np
import scipy


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

def scrape_article(urls):
    joined_text = ""
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        text_nodes = soup.find_all("div")
        joined_text += "".join(t.text.replace("\t", "").replace("\n", "") for t in text_nodes)
    return joined_text

def gourmet_scrape_article(urls):
    joined_text = ""
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        main_div = soup.find("div", class_="flexible-rstlst-main")
        if main_div:
            for list_rst in main_div.find_all("div", class_="list-rst-area-article"):
                list_rst.decompose()
            text_nodes = main_div.find_all("div")
            for t in text_nodes:
                joined_text += t.get_text(strip=True)
    return joined_text

def tourism_scrape_article(urls):
    joined_text = ""
    for url in urls:
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # 自動設定
        soup = BeautifulSoup(response.text, "html.parser")
        rank_list_div = soup.find("div", class_="rankList", id="rankList")
        if rank_list_div:
            text_nodes = rank_list_div.find_all("div")
            for t in text_nodes:
                if "item-relation-planlist" not in t.get("class", []):
                    joined_text += t.text.replace("\t", "").replace("\n", "")
    print("joined_text", joined_text)
    return joined_text


def chunk_text(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start + chunk_size <= len(text):
        chunks.append(text[start:start + chunk_size])
        start += (chunk_size - overlap)
    if start < len(text):
        chunks.append(text[-chunk_size:])
    return chunks


def vectorize_text(text):
    response = client.embeddings.create(
        input = text,
        model = "text-embedding-3-small"
    )
    return response.data[0].embedding


def cosine_similarity_manual(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)

def find_most_similar(question_vector, vectors, documents):
    similarities = []
    for index, vector in enumerate(vectors):
        similarity = cosine_similarity_manual(question_vector, vector)
        similarities.append([similarity, index])
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_documents = [documents[index] for similarity, index in similarities[:2]]
    return top_documents


def ask_question(question, context, model, message_template):
    prompt = message_template.format(question=question, context=context)
    response = client.chat.completions.create(
        # model="ft:gpt-3.5-turbo-0125:personal:inn-faq-v1:AOL3qfFi",
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content




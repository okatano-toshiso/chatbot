import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import re
import numpy as np


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
        joined_text += "".join(
            t.text.replace("\t", "").replace("\n", "") for t in text_nodes
        )
    return joined_text


def gourmet_scrape_article(urls):
    joined_text = ""
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        restaurant_divs = soup.find_all("div", class_="list-rst__wrap")
        for restaurant in restaurant_divs:
            award_badge = restaurant.find("div", class_="list-rst__award-badge")
            if award_badge:
                joined_text += "受賞歴：" + award_badge.get_text(strip=True) + "\n"
            ranking_badge = restaurant.find("i", class_="c-ranking-badge__contents")
            if ranking_badge:
                joined_text += (
                    "ランキング順位：" + ranking_badge.get_text(strip=True) + "\n"
                )
            restaurant_name = restaurant.find("a", class_="list-rst__rst-name-target")
            if restaurant_name:
                joined_text += "店舗名：" + restaurant_name.get_text(strip=True) + "\n"
            distance = restaurant.find("span", class_="list-rst__sub-area")
            if distance:
                joined_text += (
                    "交通機関からの距離：" + distance.get_text(strip=True) + "\n"
                )
            genre = restaurant.find("mark", class_="list-rst__search-keyword")
            if genre:
                joined_text += "ジャンル：" + genre.get_text(strip=True) + "\n"
            promo_text = restaurant.find("p", class_="list-rst__pr-title")
            if promo_text:
                joined_text += (
                    "プロモーション文章：" + promo_text.get_text(strip=True) + "\n"
                )
            rating = restaurant.find("span", class_="c-rating__val")
            if rating:
                joined_text += "評価点：" + rating.get_text(strip=True) + "\n"
            dinner_price = restaurant.select_one(
                "i.c-rating-v3__time--dinner + span.c-rating-v3__val"
            )
            if dinner_price:
                joined_text += "夜の価格帯：" + dinner_price.get_text(strip=True) + "\n"
            lunch_price = restaurant.select_one(
                "i.c-rating-v3__time--lunch + span.c-rating-v3__val"
            )
            if lunch_price:
                joined_text += "昼の価格帯：" + lunch_price.get_text(strip=True) + "\n"
            holiday = restaurant.find("span", class_="list-rst__holiday-text")
            if holiday:
                joined_text += "定休日：" + holiday.get_text(strip=True) + "\n"
            comment_heading = restaurant.find("a", class_="list-rst__comment-text")
            if comment_heading:
                joined_text += (
                    "コメント見出し：" + comment_heading.get_text(strip=True) + "\n"
                )
            comment_content = restaurant.select_one(
                "div.list-rst__author-rvw-txt-wrap span"
            )
            if comment_content:
                joined_text += (
                    "コメント中身：" + comment_content.get_text(strip=True) + "\n"
                )
            joined_text += "\n"
    joined_text = re.sub(r"\s", "", joined_text)
    return joined_text


def faq_scrape_article(urls):
    joined_text = ""
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        faq_divs = soup.find_all("dl", class_="typeQA")
        for faq_div in faq_divs:
            questions = faq_div.find_all("dt", class_="mod_ocmenu")
            for question in questions:
                question_text = question.get_text(strip=True)
                answer = question.find_next_sibling("dd").find("div", class_="inner").find("p")
                if answer:
                    answer_text = answer.get_text(strip=True)
                    joined_text += f"質問：{question_text}\n回答：{answer_text}\n\n"
    joined_text = re.sub(r"\s", "", joined_text)
    return joined_text


def tourism_scrape_article(urls):
    joined_text = ""
    for url_index, url in enumerate(urls):
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        item_info_divs = soup.find_all("div", class_="item-info")
        ranking_counter = 1 + (url_index * 30)
        for item_info in item_info_divs:
            h3_tag = item_info.find("h3")
            if h3_tag:
                joined_text += (
                    f"ランキング{ranking_counter}位：観光スポット："
                    + h3_tag.get_text(strip=True)
                    + "\n"
                )
                ranking_counter += 1
            review_point = item_info.find("span", class_="reviewPoint")
            if review_point:
                joined_text += (
                    "評価ポイント：" + review_point.get_text(strip=True) + "\n"
                )
            item_categories = item_info.find("p", class_="item-categories")
            if item_categories:
                joined_text += (
                    "カテゴリ：" + item_categories.get_text(strip=True) + "\n"
                )
            tag_spots = item_info.find_all("li", class_="tagSpots")
            for tag in tag_spots:
                joined_text += "タグ：" + tag.get_text(strip=True) + "\n"
            item_review_text = item_info.find("div", class_="item-reviewText")
            if item_review_text:
                joined_text += (
                    "レビュー：" + item_review_text.get_text(strip=True) + "\n"
                )
            item_desc = item_info.find("p", class_="item-desc")
            if item_desc:
                joined_text += "説明：" + item_desc.get_text(strip=True) + "\n"
            joined_text += "\n"
    joined_text = re.sub(r"\s", "", joined_text)
    return joined_text


def chunk_text(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start + chunk_size <= len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    if start < len(text):
        chunks.append(text[-chunk_size:])
    return chunks


def vectorize_text(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
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

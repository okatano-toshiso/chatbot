# utils/vocabulary_filter_utils.py

import boto3


def create_vocabulary_filter_if_not_exists():
    filter_name = "dev-commapi-trnscrb-api-LineChatBot-Filtering"
    language_code = "ja-JP"
    words = [
        "死ね",
        "殺す",
        "ファック",
        "気落ち悪い",
        "うんこ",
        "くそやろー",
        "爆破",
        "キチガイ",
        "気狂い",
        "イカレ野郎",
    ]
    transcribe_client = boto3.client("transcribe")

    try:
        transcribe_client.get_vocabulary_filter(VocabularyFilterName=filter_name)
        print(f"Vocabulary Filter '{filter_name}' already exists. No action taken.")
    except transcribe_client.exceptions.BadRequestException:
        response = transcribe_client.create_vocabulary_filter(
            VocabularyFilterName=filter_name, LanguageCode=language_code, Words=words
        )
        print(f"Vocabulary Filter Created: {response}")

    return filter_name

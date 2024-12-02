import re


def extract_number(text: str, *digit_counts) -> str:
    char_to_digit = {
        "一": "1",
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "〇": "0",
        "零": "0",
        "丸": "0",
        "壱": "1",
        "弐": "2",
        "参": "3",
        "肆": "4",
        "伍": "5",
        "陸": "6",
        "漆": "7",
        "捌": "8",
        "玖": "9",
        "ゼロ": "0",
        "イチ": "1",
        "ニ": "2",
        "サン": "3",
        "シ": "4",
        "ヨン": "4",
        "ゴ": "5",
        "ロク": "6",
        "ナナ": "7",
        "ハチ": "8",
        "キュウ": "9",
        "ク": "9",
        "レイ": "0",
        "マル": "0",
        "ぜろ": "0",
        "いち": "1",
        "さん": "3",
        "よん": "4",
        "ろく": "6",
        "なな": "7",
        "はち": "8",
        "きゅう": "9",
        "れい": "0",
        "まる": "0",
        "０": "0",
        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",
    }
    for k, v in char_to_digit.items():
        text = text.replace(k, v)
    text = re.sub(r"[^\d]", "", text)
    digit_pattern = "|".join(f"\\d{{{d}}}" for d in sorted(digit_counts, reverse=True))
    matches = re.findall(digit_pattern, text)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise False
    else:
        return False

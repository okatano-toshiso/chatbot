import re

kanji_to_digit = {
    '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
    '六': '6', '七': '7', '八': '8', '九': '9', '〇': '0', '零': '0', '丸': '0'
}

# カタカナの対応表
katakana_to_digit = {
    'ゼロ': '0', 'イチ': '1', 'ニ': '2', 'サン': '3', 'シ': '4', 'ヨン': '4', 'ゴ': '5',
    'ロク': '6', 'ナナ': '7', 'ハチ': '8', 'キュウ': '9', 'ク': '9', 'レイ': '0', 'マル': '0'
}

# ひらがなの対応表
hiragana_to_digit = {
    'ぜろ': '0', 'いち': '1', 'に': '2', 'さん': '3', 'し': '4', 'よん': '4', 'ご': '5',
    'ろく': '6', 'なな': '7', 'はち': '8', 'きゅう': '9', 'く': '9', 'れい': '0', 'まる': '0'
}

def zenkaku_to_hankaku(text: str) -> str:
    return text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))

def kanji_to_arabic(text: str) -> str:
    for kanji, digit in kanji_to_digit.items():
        text = text.replace(kanji, digit)
    return text

def katakana_to_arabic(text: str) -> str:
    for kana, digit in katakana_to_digit.items():
        text = text.replace(kana, digit)
    return text

def hiragana_to_arabic(text: str) -> str:
    for kana, digit in hiragana_to_digit.items():
        text = text.replace(kana, digit)
    return text

def clean_phone_number(phone_number: str) -> str:
    # 全角数字を半角に変換
    phone_number = zenkaku_to_hankaku(phone_number)
    # 漢数字をアラビア数字に変換
    phone_number = kanji_to_arabic(phone_number)
    # カタカナをアラビア数字に変換
    phone_number = katakana_to_arabic(phone_number)
    # ひらがなをアラビア数字に変換
    phone_number = hiragana_to_arabic(phone_number)
    # 非数字を除去してクリーンな電話番号に整形
    cleaned_number = re.sub(r'\D', '', phone_number)
    return cleaned_number

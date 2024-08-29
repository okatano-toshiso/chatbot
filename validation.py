from datetime import datetime
import re


def is_valid_date(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_single_digit_number(value: str) -> bool:
    return value.isdigit() and 0 <= int(value) <= 9


def is_valid_phone_number(phone_number: str) -> bool:
    return phone_number.isdigit() and (
        len(phone_number) == 10 or len(phone_number) == 11
    )

def is_valid_smoker(smoker: str) -> bool:
    valid_smoker = [
        "禁煙",
        "喫煙"
    ]
    return smoker in valid_smoker


def is_valid_room_type_no_smoker(room_type: str) -> bool:
    valid_room_type_no_smoker = [
        "シングル(SK)",
        "シングルA(SAK)",
        "スモールシングルA(XSK)",
        "エコノミーダブル(WAK)",
        "キングダブル(QWK)",
        "エコノミーツイン(ETK)",
        "ハートフルツイン(HTK)",
        "ハートフルシングル(HSK)",
    ]
    return room_type in valid_room_type_no_smoker


def is_valid_room_type_smoker(room_type: str) -> bool:
    valid_room_type_smoker = [
        "シングル(S)",
        "シングルA(SA)",
        "スモールシングルA(XS)",
        "エコノミーダブル(WA)",
        "キングダブル(QW)",
        "エコノミーツイン(ET)"
    ]
    return room_type in valid_room_type_smoker

def is_valid_reserve_confirm(reserve_confirm: str) -> bool:
    valid_reserve_confirm = [
        "「はい。」",
        "「ハイ。」",
        "はい。",
        "ハイ。",
        "「はい」",
        "「ハイ」",
        "はい",
        "ハイ",
        "イエス",
        "YES"
    ]
    return reserve_confirm in valid_reserve_confirm

def is_valid_reserve_number(value: int) -> bool:
    return value.isdigit() and len(value) <= 255


def is_valid_japanese_character(value: str) -> bool:
    try:
        if re.fullmatch(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+', value):
            return True
        else:
            return False
    except ValueError:
        return False


def is_valid_japanese_katakana(value: str) -> bool:
    try:
        if re.fullmatch(r'[\u30A0-\u30FF]+', value):
            return True
        else:
            return False
    except ValueError:
        return False


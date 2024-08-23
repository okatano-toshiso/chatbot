from datetime import datetime


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


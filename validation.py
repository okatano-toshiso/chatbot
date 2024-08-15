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

def is_valid_smoking(smoking: str) -> bool:
    valid_smokings = [
        "禁煙",
        "喫煙"
    ]
    return smoking in valid_smokings


def is_valid_room_type(room_type: str) -> bool:
    valid_room_types = [
        "シングル(SK)",
        "シングルA(SAK)",
        "スモールシングルA(XSK)",
        "エコノミーダブル(WAK)",
        "キングダブル(QWK)",
        "エコノミーツイン(ETK)",
        "ハートフルツイン(HTK)",
        "ハートフルシングル(HSK)",
    ]
    return room_type in valid_room_types


def is_valid_room_type_smoke(room_type: str) -> bool:
    valid_room_types = [
        "シングル(S)",
        "シングルA(SA)",
        "スモールシングルA(XS)",
        "エコノミーダブル(WA)",
        "キングダブル(QW)",
        "エコノミーツイン(ET)"
    ]
    return room_type in valid_room_types


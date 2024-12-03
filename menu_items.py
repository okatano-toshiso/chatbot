from enum import Enum


class MenuItem(Enum):
    NEW_RESERVATION = ("1", "新規宿泊予約")
    CONFIRM_RESERVATION = ("2", "予約確認")
    MODIFY_RESERVATION = ("3", "予約変更")
    CANCEL_RESERVATION = ("4", "予約キャンセル")
    FAQ = ("5", "よくある質問")
    GOURMET = ("6", "グルメ情報")
    TOURISM = ("7", "観光スポット情報")
    GUEST = ("8", "宿泊者情報")
    GREETING = ("9", "挨拶")

    def __init__(self, code, label):
        self.code = code
        self._value_ = label

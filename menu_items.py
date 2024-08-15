from enum import Enum


class MenuItem(Enum):
    NEW_RESERVATION = "新規宿泊予約"
    CONFIRM_RESERVATION = "予約確認"
    MODIFY_RESERVATION = "予約変更"
    CANCEL_RESERVATION = "予約キャンセル"
    FAQ = "よくある質問"

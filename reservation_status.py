from enum import Enum


class ReservationStatus(Enum):

    RESERVATION_MENU_INDEX = ("RESERVATION_MENU_INDEX", None)

    RESERVATION_MENU = ("RESERVATION_MENU", None)
    NEW_RESERVATION_START = ("NEW_RESERVATION_START", None)
    NEW_RESERVATION_JUDGE_INTENT = ("NEW_RESERVATION_JUDGE_INTENT", "judge_intent")
    NEW_RESERVATION_CHECKIN = ("NEW_RESERVATION_CHECKIN", "check_in")
    NEW_RESERVATION_CHECKOUT = ("NEW_RESERVATION_CHECKOUT", "check_out")
    NEW_RESERVATION_COUNT_OF_PERSON = (
        "NEW_RESERVATION_COUNT_OF_PERSON",
        "count_of_person",
    )
    NEW_RESERVATION_SMOKER = ("NEW_RESERVATION_SMOKER", "smoker")
    NEW_RESERVATION_NO_SMOKER = ("NEW_RESERVATION_NO_SMOKER", "smoker")
    NEW_RESERVATION_ROOM_TYPE = ("NEW_RESERVATION_ROOM_TYPE", "room_type")
    NEW_RESERVATION_ROOM_TYPE_SMOKER = ("NEW_RESERVATION_ROOM_TYPE_SMOKER", "room_type")
    NEW_RESERVATION_ROOM_TYPE_NO_SMOKER = (
        "NEW_RESERVATION_ROOM_TYPE_NO_SMOKER",
        "room_type",
    )
    NEW_RESERVATION_NAME = ("NEW_RESERVATION_NAME", "name")
    NEW_RESERVATION_NAME_KANA = ("NEW_RESERVATION_NAME", "name_kana")
    NEW_RESERVATION_ADULT = ("NEW_RESERVATION_ADULT", "adult")
    NEW_RESERVATION_PHONE_NUMBER = ("NEW_RESERVATION_PHONE_NUMBER", "phone_number")
    NEW_RESERVATION_RESERVE_CONFIRM = ("NEW_RESERVATION_RESERVE_CONFIRM", None)
    NEW_RESERVATION_RESERVE_EXECUTE = ("NEW_RESERVATION_RESERVE_EXECUTE", None)
    NEW_RESERVATION_RESERVE_COMPLETE = ("NEW_RESERVATION_RESERVE_COMPLETE", None)

    @property
    def key(self):
        return self.value[1]


class CheckReservationStatus(Enum):
    CHECK_RESERVATION_START = ("CHECK_RESERVATION_START", None)
    CHECK_RESERVATION_NUMBER = ("CHECK_RESERVATION_NUMBER", "reserve_id")
    CHECK_RESERVATION_NAME = ("CHECK_RESERVATION_NAME", "name")
    CHECK_RESERVATION_PHONE_NUMBER = ("CHECK_RESERVATION_PHONE_NUMBER", "phone_number")
    CHECK_RESERVATION_GET_NUMBER = ("CHECK_RESERVATION_GET_NUMBER", None)
    CHECK_RESERVATION_GET_NUMBER_MORE = ("CHECK_RESERVATION_GET_NUMBER_MORE", None)

    @property
    def key(self):
        return self.value[1]


class UpdateReservationStatus(Enum):
    UPDATE_RESERVATION_START = ("UPDATE_RESERVATION_START", None)
    UPDATE_RESERVATION_CHECKIN = ("UPDATE_RESERVATION_CHECKIN", "check_in")
    UPDATE_RESERVATION_CHECKOUT = ("UPDATE_RESERVATION_CHECKOUT", "check_out")
    UPDATE_RESERVATION_COUNT_OF_PERSON = (
        "UPDATE_RESERVATION_COUNT_OF_PERSON",
        "count_of_person",
    )
    UPDATE_RESERVATION_SMOKER = ("UPDATE_RESERVATION_SMOKER", "smoker")
    UPDATE_RESERVATION_NO_SMOKER = ("UPDATE_RESERVATION_NO_SMOKER", "smoker")
    UPDATE_RESERVATION_ROOM_TYPE = ("UPDATE_RESERVATION_ROOM_TYPE", "room_type")
    UPDATE_RESERVATION_ROOM_TYPE_SMOKER = (
        "UPDATE_RESERVATION_ROOM_TYPE_SMOKER",
        "room_type",
    )
    UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER = (
        "UPDATE_RESERVATION_ROOM_TYPE_NO_SMOKER",
        "room_type",
    )
    UPDATE_RESERVATION_NAME = ("UPDATE_RESERVATION_NAME", "new_name")
    UPDATE_RESERVATION_NAME_KANA = ("UPDATE_RESERVATION_NAME", "new_name_kana")
    UPDATE_RESERVATION_PHONE_NUMBER = (
        "UPDATE_RESERVATION_PHONE_NUMBER",
        "new_phone_number",
    )
    UPDATE_RESERVATION_CANCEL_CONFIRM = ("UPDATE_RESERVATION_CANCEL_CONFIRM", "status")
    UPDATE_RESERVATION_CANCEL_EXECUTE = ("UPDATE_RESERVATION_CANCEL_EXECUTE", "status")
    UPDATE_RESERVATION_CONFIRM = ("UPDATE_RESERVATION_CONFIRM", None)
    UPDATE_RESERVATION_EXECUTE = ("UPDATE_RESERVATION_EXECUTE", None)
    UPDATE_RESERVATION_COMPLETE = ("UPDATE_RESERVATION_COMPLETE", None)

    @property
    def key(self):
        return self.value[1]


class InquiryReservationStatus(Enum):
    INQUIRY_FAQ = ("INQUIRY_FAQ", None)
    INQUIRY_DEFAULT = ("INQUIRY_DEFAULT", None)


class GourmetReservationStatus(Enum):
    GOURMET_RESERVATION_MENU = ("GOURMET_RESERVATION_MENU", None)


class TourismReservationStatus(Enum):
    TOURISM_RESERVATION_MENU = ("TOURISM_RESERVATION_MENU", None)


class GuestReservationStatus(Enum):
    GUEST_RESERVATION_MENU = ("GUEST_RESERVATION_MENU", None)


class ErrorReservationStatus(Enum):
    ERROR_RESERVATION_MENU = ("ERROR_RESERVATION_MENU", None)

    @property
    def key(self):
        return self.value[1]

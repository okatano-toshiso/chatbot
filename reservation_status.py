from enum import Enum

class ReservationStatus(Enum):
    RESERVATION_MENU = ("RESERVATION_MENU", None)
    NEW_RESERVATION_START = ("NEW_RESERVATION_START", None)
    NEW_RESERVATION_CHECKIN = ("NEW_RESERVATION_CHECKIN", "check_in")
    NEW_RESERVATION_CHECKOUT = ("NEW_RESERVATION_CHECKOUT", "check_out")
    NEW_RESERVATION_COUNT_OF_PERSON = ("NEW_RESERVATION_COUNT_OF_PERSON", "count_of_person")
    NEW_RESERVATION_SMOKER = ("NEW_RESERVATION_SMOKER", "smoker")
    NEW_RESERVATION_NO_SMOKER = ("NEW_RESERVATION_NO_SMOKER", "smoker")
    NEW_RESERVATION_ROOM_TYPE = ("NEW_RESERVATION_ROOM_TYPE", "room_type")
    NEW_RESERVATION_ROOM_TYPE_SMOKER = ("NEW_RESERVATION_ROOM_TYPE_SMOKER", "room_type")
    NEW_RESERVATION_ROOM_TYPE_NO_SMOKER = ("NEW_RESERVATION_ROOM_TYPE_NO_SMOKER", "room_type")
    NEW_RESERVATION_NAME = ("NEW_RESERVATION_NAME", "name")
    NEW_RESERVATION_PHONE_NUMBER = ("NEW_RESERVATION_PHONE_NUMBER", "phone_number")
    NEW_RESERVATION_RESERVE_CONFIRM = ("NEW_RESERVATION_RESERVE_CONFIRM", None)
    NEW_RESERVATION_RESERVE_EXECUTE = ("NEW_RESERVATION_RESERVE_EXECUTE", None)
    NEW_RESERVATION_RESERVE_COMPLETE = ("NEW_RESERVATION_RESERVE_COMPLETE", None)
    @property
    def key(self):
        return self.value[1]


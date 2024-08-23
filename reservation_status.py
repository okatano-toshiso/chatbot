from enum import Enum

class ReservationStatus(Enum):
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

    @property
    def key(self):
        return self.value[1]


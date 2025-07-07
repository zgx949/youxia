import config
import copy


def search(search_key: str):
    """
    通过城市名称、酒店名称搜索，会出现模糊匹配的酒店

    :return:
    """
    data = {
        "searchKey": search_key
    }
    response = config.post("/openapi/hotel/suggest", json=data)
    hotelEsList = response["hotelEsList"]
    return hotelEsList


# 找到含早餐的最低价
def clean_room_detail(detail):
    detail = copy.deepcopy(detail)
    for key in ["interests", "rateRangeList", "paymentType", "storeExtra"]:
        detail.pop(key, None)
    return detail


def get_room_price(hotelId: int, checkin: str, checkout: str, adultNum: int = 2):
    """
    获取酒店房型房价列表，通过酒店id+入住时间+离店时间+成人数获取

    :param hotelId:
    :param checkin:
    :param checkout:
    :param adultNum:
    :return:
    """

    data = {
        "hotelId": hotelId,
        "checkin": checkin,
        "checkout": checkout,
        "adultNum": adultNum
    }
    priceList = config.post("/openapi/hotel/listRatePlan", json=data)
    result = []
    for item in priceList:
        temp_data = copy.deepcopy(item)
        del temp_data["hotelRoomDetails"]
        hotelRoomDetails = item["hotelRoomDetails"]

        breakfast_room_details = None
        no_breakfast_room_details = None

        for room in hotelRoomDetails:
            if room["breakfast"] == 1 and breakfast_room_details is None:
                breakfast_room_details = clean_room_detail(room)
            elif room["breakfast"] == 0 and no_breakfast_room_details is None:
                no_breakfast_room_details = clean_room_detail(room)
            if breakfast_room_details and no_breakfast_room_details:
                break

        temp_data["hotelRoomDetails"] = []
        if breakfast_room_details:
            temp_data["hotelRoomDetails"].append(breakfast_room_details)
        if no_breakfast_room_details:
            temp_data["hotelRoomDetails"].append(no_breakfast_room_details)
        result.append(temp_data)

    return result

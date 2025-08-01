import json

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


def generate_room_text(room: dict, checkin_date: str, checkout_date: str):
    # 房型行
    room_name = room.get("name", "未知房型")
    room_line = f"房型：{room_name}"

    # 入住天数
    from datetime import datetime
    d1 = datetime.strptime(checkin_date, "%Y-%m-%d")
    d2 = datetime.strptime(checkout_date, "%Y-%m-%d")
    nights = (d2 - d1).days

    # 每种方案一行
    price_lines = []
    for detail in room.get("hotelRoomDetails", []):
        total = detail.get("totalPrice", 0)
        breakfast = "含早餐" if detail.get("breakfast") else "无早餐"
        per_night = round(total / nights, 2) if nights else total
        plan_name = detail.get("name", "")
        line = f"价格：CNY {total:.2f}（{per_night:.0f}每晚）｜{breakfast}｜{plan_name}"
        # line = f"- 价格：CNY {total:.2f}｜{breakfast}｜{plan_name}"
        price_lines.append(line)

    # 组合文本
    final_text = "\n".join([room_line] + price_lines)
    return final_text


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
    result_text = ''
    for room in result:
        result_text += generate_room_text(room, checkin, checkout)+'\n'
    return result_text

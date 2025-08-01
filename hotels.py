import json
from datetime import datetime
import config
import copy
from rapidfuzz import fuzz, process


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


def get_rooms(room_type, rooms):
    scores = process.extract(room_type, rooms, scorer=fuzz.ratio, limit=None)
    matched = [(item, score) for (item, score, _) in scores if (scores[0][1] >= 70 and scores[0][1] - score <= 10) or (
            scores[0][1] < 70 and scores[0][1] - score <= 25)]  # 与分数最高项相比差别不大也选择
    if len(matched) == 0:  # 没有匹配到的话，全部返回
        matched = [(room, 100) for room in rooms]
    return [item[0] for item in matched]


def generate_room_text(room: dict, checkin_date: str, checkout_date: str):
    # 房型行
    room_name = room.get("name", "未知房型")
    room_name = room_name.replace('面积', '').replace('床宽', '床')
    # room_name = room_name.split('（')[0]
    room_line = f"{room_name}"

    # 入住天数
    from datetime import datetime
    d1 = datetime.strptime(checkin_date, "%Y-%m-%d")
    d2 = datetime.strptime(checkout_date, "%Y-%m-%d")
    nights = (d2 - d1).days

    price_lines = []
    with_breakfast = None
    without_breakfast = None

    for detail in room.get("hotelRoomDetails", []):
        total = detail.get("totalPrice", 0)
        breakfast = detail.get("breakfast")
        line = f"{'- 含早' if breakfast else '- 无早'}: CNY {total:.2f}"

        if breakfast:
            if with_breakfast is None or total < with_breakfast[0]:
                with_breakfast = (total, line)
        else:
            if without_breakfast is None or total < without_breakfast[0]:
                without_breakfast = (total, line)

    # 判断差价是否超过 200 元
    if with_breakfast and without_breakfast:
        price_diff = abs(with_breakfast[0] - without_breakfast[0])
        if price_diff > 200:
            price_lines.append(with_breakfast[1])
            price_lines.append(without_breakfast[1])
        else:
            price_lines.append(with_breakfast[1])
    elif with_breakfast:
        price_lines.append(with_breakfast[1])
    elif without_breakfast:
        price_lines.append(without_breakfast[1])

    # 组合文本
    final_text = "\n".join([room_line] + price_lines)
    return final_text


seq_icons = [
    '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩',
    '⑪', '⑫', '⑬', '⑭', '⑮', '⑯', '⑰', '⑱', '⑲', '⑳'
]


def get_room_price(hotelId: str, checkin: str, checkout: str, adultNum: int = 2, hotel_name="", room_type=""):
    """
    获取酒店房型房价列表，通过酒店id+入住时间+离店时间+成人数获取

    :param hotel_name:
    :param room_type:
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

    # 计算间夜数量
    begin_date = datetime.strptime(checkin, "%Y-%m-%d")
    end_date = datetime.strptime(checkout, "%Y-%m-%d")
    night_count = (end_date - begin_date).days

    result_text = (f'酒店名：{hotel_name}\n'
                   f'入住时间: {begin_date.year}-{begin_date.month}-{begin_date.day}\n'
                   f'离店时间: {end_date.year}-{end_date.month}-{end_date.day}\n'
                   f'间夜数: {night_count}\n\n'
                   )
    rooms = [room['name'].split('（')[0].replace('客房', '房') for room in result]
    matched_rooms = get_rooms(room_type, rooms)
    i = 0
    for room in result:
        room_name = room['name'].replace('客房', '房')
        if room_name.split('（')[0] in matched_rooms:
            result_text += seq_icons[i] + generate_room_text(room, checkin, checkout) + '\n'
            i += 1
        # 未指定房型，只返回一个数据
        if not room_type or len(matched_rooms) == len(rooms):
            break
    result_text += """
尊享权益：
• 每日双人早餐
• 视房态升级房型(套房除外)
• 视房态提前入住或延迟退房
• 免费Wi-Fi 
• 迷你吧(免费享受酒店迷你吧软饮)
• 单程接送机(豪华海景双卧联通套房、豪华海景泳池套房、全海景泳池套房、双卧海景家庭套房-萌能主题房型，预订可享三亚机场至酒店专车接机或送机1次；至少提前1天预约)
• 额外额度(全海景房及以上房型，预订可享200元水疗消费额度1份)
• 额外礼遇(海景泳池房及以上房型，预订可享每日东厨日落时光小食(含软饮)1份)
    """
    return result_text

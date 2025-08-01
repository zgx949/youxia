import hotels

items = hotels.search("杭州")
for item in items:
    id = item.get("id")
    name = item.get("name")
    resp = hotels.get_room_price(id, "2025-08-16", "2025-08-18", 2, "三亚亚龙湾瑞吉酒店", '豪华房')
    print(resp)
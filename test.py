import hotels

items = hotels.search("杭州")
for item in items:
    id = item.get("id")
    resp = hotels.get_room_price(id, "2025-07-16", "2025-07-18")
    print(resp)
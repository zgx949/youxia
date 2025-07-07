import httpx
from mcp.server.fastmcp import FastMCP

import hotels

# Initialize FastMCP server
mcp = FastMCP("hotels")


@mcp.tool()
async def search_hotels(hotel_name: str) -> list:
    """模糊搜索酒店

    :param hotel_name: 酒店关键词
    :return:
    """

    data = hotels.search(hotel_name)
    return data

@mcp.tool()
async def query_hotel_room_details(hotel_id: int, checkin_date: str, checkout_date: str) -> list:
    """查询酒店价格

    :param hotel_id:
    :param checkin_date:
    :param checkout_date:
    :return:
    """
    data = hotels.get_room_price(hotel_id, checkin_date, checkout_date)
    return data

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

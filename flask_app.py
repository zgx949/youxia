from datetime import datetime, timedelta
import os

from flask import Flask, request, jsonify, abort, send_from_directory
from hotels import search, get_room_price  # 替换为你定义函数的模块名

# 指定静态页面目录路径
PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')

app = Flask(__name__)


@app.route('/search', methods=['GET'])
def search_hotels():
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Missing 'key' parameter"}), 400

    try:
        results = search(key)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/room_price', methods=['GET'])
def room_price():
    try:
        hotel_id = int(request.args.get('hotelId'))
        checkin = request.args.get('checkin', datetime.today().strftime('%Y-%m-%d'))
        checkout = request.args.get('checkout', (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d'))
        adult_num = int(request.args.get('adultNum', 2))

        if not (hotel_id and checkin and checkout):
            return jsonify({"error": "Missing parameters"}), 400

        result = get_room_price(hotel_id, checkin, checkout, adult_num)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/pages/<path:filename>', methods=['GET'])
def get_pages(filename):
    if not filename.endswith('.html'):
        abort(404)
    try:
        return send_from_directory(PAGES_DIR, filename)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)

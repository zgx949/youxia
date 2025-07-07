import base64
import time
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import os
from dotenv import load_dotenv  # 新增

load_dotenv()
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
BASE_URL = os.getenv("BASE_URL")


def aes_encrypt(data, key) -> str:
    """
    使用 AES/ECB/PKCS7Padding 加密数据
    """
    data = data.encode('utf-8')
    key = key.encode('utf-8')

    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pad(data, AES.block_size)  # 👈 使用 PKCS7 padding
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')


def get_token() -> Optional[str]:
    """
    获取token

    :return:
    """
    timestamps = int(time.time() * 1000)
    sign_data = APP_KEY + APP_SECRET + str(timestamps)
    sign = aes_encrypt(sign_data, APP_SECRET)

    request_data = {
        "appKey": APP_KEY,
        "appSecert": APP_SECRET,
        "timestamps": timestamps,
        "sign": sign
    }

    response = requests.post(BASE_URL + '/openapi/auth/getToken', json=request_data)

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0 and data.get("msg") == "SUCCESS":
            return data["data"]
        print("获取 Token 失败：", data.get("msg"))
    else:
        print("请求失败：", response.status_code, response.text)

    return None


TOKEN = get_token()

session = requests.Session()


def response_hook(response, *args, **kwargs):
    return response


# 只支持 response
session.hooks['response'] = [response_hook]


def __do_request__(method: str, path: str, retry: int = 3, **kwargs):
    if retry <= 0:
        raise Exception("多次刷新Token失败，请检查环境变量")

    global TOKEN

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = TOKEN
    if method == "GET":
        response = session.post(BASE_URL + path, headers=headers, **kwargs)
    elif method == "POST":
        response = session.post(BASE_URL + path, headers=headers, **kwargs)
    else:
        raise ValueError("Invalid method, must be GET or POST")

    if not response.ok:  # 非 2xx
        response.raise_for_status()  # 抛出 HTTPError，自动带有 status_code 和 text

    data = response.json()
    msg = data.get("msg")
    code = data.get("code")
    if code == 0 and msg == "SUCCESS":
        return data["data"]
    elif code == -1 and msg == "SYSTEM_ERROR->token失效":
        # 刷新TOKEN
        TOKEN = get_token()
        return __do_request__(method, path, retry-1, **kwargs)
    else:
        raise Exception(f"API返回错误: {data.get('msg')}")


def get(path: str, **kwargs):
    return __do_request__("GET", path, **kwargs)


def post(path: str, **kwargs):
    return __do_request__("POST", path, **kwargs)

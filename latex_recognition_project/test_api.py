'''
Author: Maggie xungirl1024@gmail.com
Date: 2024-11-15 11:32:38
LastEditors: Maggie xungirl1024@gmail.com
LastEditTime: 2024-11-15 13:25:15
FilePath: /latex_recognition_project/test_api.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import requests
import json

# 配置 API 相关信息
API_TOKEN = "KGdAEDop1kAwRtPlb9ytokYW9efprvCqRiUzTtDkqc32ylbgX5fbGILYl19AFfXx"
API_URL = "https://server.simpletex.cn/api/latex_ocr" # 替换为实际的 API URL

# 请求头和文件
headers = {"token": API_TOKEN}
data = {}  # 如果有其他请求参数，可以在这里添加

# 打开测试文件并发送请求
try:
    with open("test.png", "rb") as file:
        files = {"file": ("test.png", file, "image/png")}
        response = requests.post(API_URL, files=files, data=data, headers=headers)
        response.raise_for_status()  # 检查是否有HTTP错误

        # 打印返回的 JSON 数据
        print("API Response:", json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print("API Request failed:", str(e))
except FileNotFoundError:
    print("Error: 'test.png' file not found.")
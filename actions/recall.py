import requests

from config import API_URL,TOKEN

def recall(chat_id, msg_id):
    data = {
        "msgId": str(msg_id),
        "chatId": str(chat_id),
        "chatType": "group"  # 根据实际情况改
    }
    response = requests.post(f"{API_URL}/recall?token={TOKEN}", json=data)
    print(response.status_code)
    print(response.json())
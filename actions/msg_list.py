import requests
from datetime import datetime
from config import TOKEN,API_URL


def get_messages(chat_id, chat_type="group", before=0, after=0, message_id=None):
    """
    获取并格式化消息列表
    :param chat_id: 群ID或用户ID
    :param chat_type: group 或 user
    :param before: 消息ID前N条
    :param after: 消息ID后N条
    :param message_id: 基准消息ID（可选）
    :return: 格式化后的消息列表（list of str）
    """
    params = {
        "token": TOKEN,
        "chat-id": chat_id,
        "chat-type": chat_type,
    }
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    if message_id:
        params["message-id"] = message_id

    try:
        resp = requests.get(f"{API_URL}/messages", params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"获取消息失败: {e}")
        return []

    if data.get("code") != 1:
        print(f"API返回错误: {data.get('msg')}")
        return []

    formatted_msgs = []
    for msg in data["data"].get("list", []):
        sender = msg.get("senderNickname", "未知")
        content_type = msg.get("contentType", "")
        send_time = datetime.fromtimestamp(msg.get("sendTime", 0) / 1000).strftime("%Y-%m-%d %H:%M:%S")

        if content_type in ("text", "markdown"):
            text = msg["content"].get("text", "")
        else:
            text = f"[{content_type}]"

        formatted_msgs.append(f"[{send_time}] {sender}: {text}")

    return formatted_msgs

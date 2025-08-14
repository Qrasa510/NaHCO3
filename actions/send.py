import os
from io import BytesIO

import requests
from config import API_URL, TOKEN


def sendmsg(chat_id, content_type, content, parent="", buttons=None):
    if buttons is None:
        buttons = []

    data = {
        "recvId": str(chat_id),
        "recvType": "group",
        "contentType": str(content_type),
        "parentId": str(parent),
        "content": None
    }

    if content_type in ["text", "html", "markdown"]:
        data["content"] = { # type: ignore
            "text": str(content),
            "buttons": buttons
        }
    elif content_type in ["image", "video", "file"]:
        data["content"] = { # type: ignore
            f"{content_type}Key": str(content),
            "buttons": buttons
        }
    else:
        data["content"] = {"text": str(content)}

    response = requests.post(f"{API_URL}/send?token={TOKEN}", json=data)
    print(response.status_code)
    print(response.json())
    return 


def uploadimg(chat_id, image_source, from_disk=False):
    """
    上传图片到服务器并发送

    :param chat_id: 聊天ID
    :param image_source: 本地图片路径、网络图片URL，或BytesIO文件对象
    :param from_disk: True表示image_source是本地路径，
                      False表示是网络URL或文件对象（由类型判断）
    :return: 成功返回imageKey字符串，失败返回False
    """
    upload_url = f"https://chat-go.jwzhd.com/open-apis/v1/image/upload?token={TOKEN}"

    try:
        if from_disk:
            # 从本地读取文件
            with open(image_source, "rb") as f:
                files = {'image': (os.path.basename(image_source), f, 'application/octet-stream')}
                response = requests.post(upload_url, files=files)
        else:
            if isinstance(image_source, str):
                # 从网络下载图片
                resp = requests.get(image_source, timeout=5)
                resp.raise_for_status()
                file_obj = BytesIO(resp.content)
                file_obj.name = "image.jpg"  # 必须带文件名
                files = {'image': (file_obj.name, file_obj, 'application/octet-stream')}
                response = requests.post(upload_url, files=files)
            else:
                # 传入了文件对象，直接上传
                image_source.seek(0)
                files = {
                    'image': (getattr(image_source, 'name', 'image.jpg'), image_source, 'application/octet-stream')}
                response = requests.post(upload_url, files=files)
    except Exception as e:
        print(f"图片上传过程出现异常: {e}")
        return False

    if response.status_code == 200:
        res_json = response.json()
        if res_json.get('code') == 1:
            image_key = res_json['data']['imageKey']
            # 发送图片消息
            data = {
                "recvId": str(chat_id),
                "recvType": "group",
                "contentType": "image",
                "content": {
                    "imageKey": image_key
                }
            }
            send_response = requests.post(f"{API_URL}/send?token={TOKEN}", json=data)
            print(send_response.status_code, send_response.json())
            return image_key
        else:
            print(f"图片上传失败: {res_json.get('msg')}")
    else:
        print(f"HTTP错误: {response.status_code}")

    return False

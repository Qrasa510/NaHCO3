import requests
import cv2
import numpy as np
from pyzbar.pyzbar import decode

from actions.send import sendmsg
from modules.bilibili_link import bililink
from modules.github_link import githublink
from modules.word_filter import check_and_recall



def qrcode(chat_id, url, msg_id):

    try:
        # 下载图片
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        # 将图片数据转换成 OpenCV 格式
        img_array = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 解码二维码
        decoded_objects = decode(img)



        if not decoded_objects:
            return  # 没有识别到二维码

        for obj in decoded_objects:

            qr_data = obj.data.decode("utf-8")

            buttons = [[
                {
                    "text": "复制文本",
                    "actionType": 2,
                    "value": qr_data
                },
            ]]

            print(f"[QR Detected] chat_id={chat_id}, msg_id={msg_id}, data={qr_data}")


            if check_and_recall(chat_id, msg_id, qr_data):
                return
            elif bililink(chat_id,qr_data):
                return
            elif githublink(chat_id,qr_data):
                return
            else:
                sendmsg(chat_id,"text",qr_data,msg_id,buttons)
    except Exception as e:
        print(f"二维码识别出错: {e}")

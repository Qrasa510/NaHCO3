import requests
import cv2
import numpy as np
import pytesseract

from modules.word_filter import check_and_recall


def ocr(chat_id, url, msg_id):
    try:
        # 下载图片
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        # 转成 OpenCV 图像
        img_array = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 转灰度提升识别率
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # OCR 识别
        text = pytesseract.image_to_string(gray, lang='chi_sim+eng')  # 中文+英文

        # 去除空白符
        text = text.strip()

        if not text:
            return  # 没识别到文字

        print(f"[OCR Detected] chat_id={chat_id}, msg_id={msg_id}, text={text}")

        check_and_recall(chat_id,msg_id,text)

    except Exception as e:
        print(f"OCR 识别出错: {e}")

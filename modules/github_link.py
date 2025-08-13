import re
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from actions.send import sendmsg, uploadimg  # 支持内存上传的函数

def githublink(chat_id, content):
    pattern = r'https?://github\.com/([\w\-]+)/([\w\-]+)(?:/|$)'
    match = re.search(pattern, content)
    if not match:
        return False

    owner, repo = match.group(1), match.group(2)
    repo_url = f"https://github.com/{owner}/{repo}"

    try:
        # 请求仓库主页HTML
        response = requests.get(repo_url, timeout=5)
        response.raise_for_status()
        html = response.text

        # 解析meta og:image
        soup = BeautifulSoup(html, "html.parser")
        og_image = soup.find("meta", property="og:image")
        if not og_image or not og_image.get("content"):
            print("未找到OG图片")
            return False

        image_url = og_image["content"]
        # 下载图片
        img_resp = requests.get(image_url, timeout=5)
        img_resp.raise_for_status()
        img_bytes = BytesIO(img_resp.content)
        img_bytes.name = f"{owner}_{repo}.png"

        # 上传图片并发送
        image_key = uploadimg(chat_id, img_bytes, from_disk=False)
        if not image_key:
            print("上传图片失败")
            return False

        # uploadimg函数一般已发送消息，这里可选是否重复发送
        sendmsg(chat_id, "image", {"imageKey": image_key})

        return True

    except Exception as e:
        print(f"处理GitHub卡片出错: {e}")
        return False

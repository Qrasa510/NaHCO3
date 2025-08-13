import re
import requests
from actions.send import sendmsg

# AV to BV
table = list('fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF')
tr = {c: i for i, c in enumerate(table)}
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608

def av2bv(av_num):
    # AV in
    r = list('BV1  4 1 7  ')
    x = (av_num ^ xor) + add
    for i in range(6):
        r[s[i]] = table[x // 58**i % 58]
    return ''.join(r)

def bililink(chat_id, content):
    bv_pattern = r'(BV[0-9A-Za-z]{10})'
    av_pattern = r'(av(\d+))'
    b23_pattern = r'(https?://b23\.tv/\S+)'

    # match BV
    bv_match = re.search(bv_pattern, content)
    if bv_match:
        bv = bv_match.group(1)
        link = f"https://www.bilibili.com/video/{bv}/"
        sendmsg(chat_id, "text", link)
        return True

    # match AV
    av_match = re.search(av_pattern, content, re.IGNORECASE)
    if av_match:
        av_num = int(av_match.group(2))
        bv = av2bv(av_num)
        link = f"https://www.bilibili.com/video/{bv}/"
        sendmsg(chat_id, "text", link)
        return True

    # match b23
    b23_match = re.search(b23_pattern, content)
    if b23_match:
        short_url = b23_match.group(1)
        try:
            response = requests.head(short_url, allow_redirects=True, timeout=5)
            final_url = response.url
            bv_match = re.search(bv_pattern, final_url)
            if bv_match:
                bv = bv_match.group(1)
                link = f"https://www.bilibili.com/video/{bv}/"
            else:
                link = final_url
            sendmsg(chat_id, "text", link)
            return True
        except requests.RequestException:
            return False

    return False

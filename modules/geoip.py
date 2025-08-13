import re
import requests
import html as html_lib
from actions.send import sendmsg
from config import BOT_NAME

def geoip(chat_id, content):
    """
    从文本中提取 IPv4 / IPv6 并查询地理位置 + 运营商，发送到群聊（所有结果折叠在一个折叠框里）
    最多处理 10 个 IP，结果拼接成一条 HTML 折叠消息发送
    """
    ipv4_pattern = r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ipv6_pattern = (
        r"\b(?:(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,7}:"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2}"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3}"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4}"
        r"|(?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5}"
        r"|[A-Fa-f0-9]{1,4}:(?:(?::[A-Fa-f0-9]{1,4}){1,6})"
        r"|:(?:(?::[A-Fa-f0-9]{1,4}){1,7}|:))\b"
    )

    ipv4_matches = re.findall(ipv4_pattern, content)
    ipv6_matches = re.findall(ipv6_pattern, content)

    seen = set()
    ips = []
    for ip in ipv4_matches + ipv6_matches:
        if ip not in seen:
            seen.add(ip)
            ips.append(ip)

    if not ips:
        return False

    truncated = False
    if len(ips) > 10:
        ips = ips[:10]
        truncated = True

    results = []
    for ip in ips:
        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                country = data.get("country", "未知")
                region = data.get("regionName", "")
                city = data.get("city", "")
                isp = data.get("isp", "未知")
                loc_parts = [country, region, city]
                loc = " ".join(p for p in loc_parts if p).strip() or "未知"
                result_text = f"IP: {ip}\n位置: {loc}\n运营商: {isp}"
            else:
                msg = data.get("message", "未找到信息")
                result_text = f"IP: {ip}\n查询失败: {msg}"
        except Exception as e:
            result_text = f"IP: {ip}\n查询出错: {str(e)}"
        results.append(result_text)

    header = f"一次最多显示前 10 个 IP，已截取。\n\n" if truncated else ""
    all_results_text = header + "\n\n".join(results)
    safe_results_html = html_lib.escape(all_results_text).replace("\n", "<br>")

    html_payload = (
        f'<details>'
        f'<summary>{BOT_NAME}帮你查到了 {len(ips)} 个 IP</summary>'
        f'<div style="margin-top:8px; white-space:pre-wrap;">{safe_results_html}</div>'
        f'</details>'
    )

    sendmsg(chat_id, "html", html_payload)
    return True

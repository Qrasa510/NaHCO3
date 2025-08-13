import requests
from actions.msg_list import get_messages
from actions.send import sendmsg
from config import GPT_KEY,BOT_NAME,GPT_PROMPT,GPT_API

def gpt(chat_id, content):
    trigger_keywords = [BOT_NAME] #可以添加其他唤起GPT的词
    if not any(kw in content for kw in trigger_keywords):
        return

    formatted_msgs = get_messages(chat_id,"group",5,0)
    content = f"{GPT_PROMPT}\n下面是最新的消息：\n{formatted_msgs}"

    print(formatted_msgs)
    url = GPT_API
    headers = {
        "Authorization": f"Bearer {GPT_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": content}],
        "temperature": 1,
        "max_tokens": 750
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if reply:
            sendmsg(chat_id, "text", reply)
    except requests.exceptions.RequestException as e:
        print(f"调用 GPT API 时发生错误: {e}")
        if e.response is not None:
            print("响应内容：", e.response.text)

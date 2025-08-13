from flask import Flask, request

from modules.bilibili_link import bililink
from modules.geoip import geoip
from modules.github_link import githublink
from modules.qrcode import qrcode
from modules.word_filter import check_and_recall
from modules.gpt_reply import gpt
from modules.ocr import ocr
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"[收到 JSON] {data}")

    # header = data.get('header', {})
    # header_eventid = data.get('eventId')
    event = data.get('event', {})

    sender = event.get('sender', {})
    sender_nickname = sender.get('senderNickname')
    # sender_id = sender.get('senderId')

    chat = event.get('chat', {})
    chat_chatid = chat.get('chatId',{})
    # chat_chattype = chat.get('chatType')

    event_message = event.get('message', {})
    event_message_id = event_message.get('msgId')
    event_message_content = event_message.get('content', {})
    event_message_content_text = event_message_content.get('text', {})
    event_message_content_imageurl = event_message_content.get('imageUrl', {})
    event_message_contenttype = event_message.get('contentType')

    if event_message_contenttype == "text":
        content = event_message_content_text
    elif event_message_contenttype == "image":
        content = event_message_content_imageurl
    else:
        return

    handle_events(chat_chatid,event_message_id,content,event_message_contenttype)
    print(sender_nickname,":",content)

    return{"status": "ok"}





def handle_events(chat_id, msg_id, content,content_type):

    print(content_type)
    if content_type == "text":
        #fuck off 屏蔽词
        if check_and_recall(chat_id, msg_id, content):
            return
        #render fucking bili解析
        bililink(chat_id,content)
        #render fucking gh解析
        githublink(chat_id,content)
        #render fucking ip解析
        geoip(chat_id,content)
        #gpt reply like shit
        gpt(chat_id,content)
    elif content_type == "image":
        #自动ocr
        ocr(chat_id,content,msg_id)
        #自动qrcode
        qrcode(chat_id,content,msg_id)
        return


if __name__ == "__main__":
    app.run(debug=True)

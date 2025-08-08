from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

from dotenv import load_dotenv
import os

load_dotenv() 
app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return callback()  # 直接重用你的 callback 邏輯
    return "✅ Line Bot is running. Webhook is at /callback"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature', None)
    if signature is None:
        abort(400)

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text in ['文字', 'text', 'Text']:
            reply = TextMessage(text='這是純文字')
        elif text in ['表情', '表情符號', 'Emoji', 'emoji']:
            emojis = [
                Emoji(index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
                Emoji(index=12, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002")
            ]
            reply = TextMessage(text="$ LINE 表情符號 $", emojis=emojis)
        elif text in ['圖片','猩猩', '星星']:
            BASE_URL = 'https://next-hub-oa.vercel.app'
            url = f"{BASE_URL}/static/Chimpanzees.jpg"
            app.logger.info(f"url={url}")
            reply = ImageMessage(original_content_url=url, preview_image_url=url)
        elif text in ['位置', '在哪', 'location', 'Location']:
            reply = LocationMessage(title='我在這', address='台灣大學德田館', latitude=25.0194301, longitude=121.5389677) 
        # else:
        #     reply = TextMessage(text=f'我重複你的話：{text}')

        if reply is None:
            reply = TextMessage(text=f'未知指令：{text}')

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token, 
                messages=[reply])
        )
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2025)
from fastapi import FastAPI, Request,BackgroundTasks, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage
from starlette.exceptions import HTTPException
import os
import random
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

@app.get("/")
def root():
    return {"title": "Echo Bot"}    
    
@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
):
    body = await request.body()

    try:
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "ok"


@handler.add(MessageEvent)
def handle_message(event):
    if event.type != "message" or event.message.type != "text":
        return
    
    message_text = event.message.text.lower()
    
    if "写真" in message_text:
        send_random_photo(event.reply_token)
    else:
        message = TextMessage(text=event.message.text + " hello")
        line_bot_api.reply_message(event.reply_token, message)

def send_random_photo(reply_token):
    photo_directory = "images1"  # 写真が格納されているディレクトリ
    photos = os.listdir(photo_directory)
    photo_path = os.path.join(photo_directory, random.choice(photos))

    # 画像を送信する
    message = ImageSendMessage(
        original_content_url=photo_path,
        preview_image_url=photo_path
    )
    line_bot_api.reply_message(reply_token, message)
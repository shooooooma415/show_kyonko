from fastapi import FastAPI, Request,BackgroundTasks, Header
from fastapi.responses import FileResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage
from starlette.exceptions import HTTPException
import os
import random
from dotenv import load_dotenv
import linebot.v3.messaging as bot
import time
import linebot.v3.messaging
from linebot.v3.messaging.models.broadcast_request import BroadcastRequest
from linebot.v3.messaging.rest import ApiException
from pprint import pprint

load_dotenv()

app = FastAPI()
LINE_BOT_API = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
LINE_USER_ID = os.getenv('LINE_USER_ID')


@app.get("/")
def root():
    return {"title": "Echo Bot"}


@app.get("/images{j}/{file_name}") # @ : アノテーションと呼ぶ
async def read_item(j:str, file_name:str):
    img_url = FileResponse(path ="./images" + j + "/" + file_name, media_type="image/jpg")
    return img_url

configuration = bot.Configuration(
    access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
)


@app.get("/send")
async def send_message():
    directory_number_list = list(range(0, 79))
    n = random.choice(directory_number_list)
    files = os.listdir(f'./images{n}')
    random_image_url = "https://show-kyonkouvi.onrender.com/" + f"images{n}/" + random.choice(files)
    
    message_dict = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": random_image_url,
                "previewImageUrl": random_image_url
            }
        ]
    }

    with bot.ApiClient(configuration) as api:
        api_instance = bot.MessagingApi(api)
        push_message_request = bot.PushMessageRequest.from_dict(message_dict)
        try:
            res = api_instance.push_message(push_message_request)
            print("Successful sending!!")
            print(res)
        except Exception as e:
            print(f"Exception: {e}")

# @app.get("/broadcast")
# async def broadcast_image():
    # configuration = linebot.v3.messaging.Configuration(host = "https://api.line.me")
    # configuration = linebot.v3.messaging.Configuration(access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    
    # with linebot.v3.messaging.ApiClient(configuration) as api_client:
    #     # Create an instance of the API class
    #     api_instance = linebot.v3.messaging.MessagingApi(api_client)
    #     broadcast_request = linebot.v3.messaging.BroadcastRequest()
    #     x_line_retry_key = 'x_line_retry_key_example'
    #     try:
    #         api_response = api_instance.broadcast(broadcast_request, x_line_retry_key=x_line_retry_key)
    #         print("The response of MessagingApi->broadcast:\n")
    #         pprint(api_response)
    #     except Exception as e:
    #         print("Exception when calling MessagingApi->broadcast: %s\n" % e)

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
    
    if "プロフィール" in message_text:
        message = TextMessage(text="齊藤京子さんについて紹介します！\n齊藤京子\n1997年9月5日生\n4/5 齊藤京子卒業コンサート in 横浜スタジアム にて日向坂46を卒業\n5/1~ 東宝芸能所属")#ここにプロフィールを流すようにするあとでかくor写真を添付
        LINE_BOT_API.reply_message(event.reply_token, message)
        
    elif "写真" in message_text or "しゃしん" in message_text:
        directory_number_list = list(range(0, 79)) #ディレクトリを指定するため
        n=random.choice(directory_number_list)
        files = os.listdir(f'./images{n}')
        random_image_url = "https://show-kyonkouvi.onrender.com/" + f"images{n}/" + random.choice(files)
        message = ImageSendMessage(
            original_content_url = random_image_url,
            preview_image_url = random_image_url
        )
        
        LINE_BOT_API.reply_message(event.reply_token, message)
        
    
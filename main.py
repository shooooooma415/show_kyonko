from fastapi import FastAPI, Request,BackgroundTasks, Header
from fastapi.responses import FileResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage
from starlette.exceptions import HTTPException
import os
import random #あとでランダムに写真を選択する用
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

directory_number_list = list(range(0, 10)) #ディレクトリを指定するため

@app.get("/")
def root():
    return {"title": "Echo Bot"}


@app.get("/images{j}/{file_name}") # @ : アノテーションと呼ぶ
async def read_item(j:str, file_name:str):
    img_url = FileResponse(path ="./images" + j + "/" + file_name, media_type="image/jpg")
    return img_url



# #listが返ってくる
# def response_image_list():
#     # 表示したいディレクトリのパスを指定
#     directory = 'file2/images1'

#     # ファイルとディレクトリの一覧を取得
#     files = os.listdir(directory)

#     responses = list()
    
#     for file in files:
#         file_path = os.path.join(directory, file)
#         responses.append(FileResponse(path=file_path, media_type="image/jpg"))
    
#     return responses
    
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
        line_bot_api.reply_message(event.reply_token, message)
    elif "写真" in message_text:
        directory_number_list = list(range(0, 10)) #ディレクトリを指定するため
        n=random.choice(directory_number_list)
        files = os.listdir('./images{n}')
        random_image_url = "https://show-kyonkouvi.onrender.com/" + f"images{n}/" + random.choice(files)
        message = ImageSendMessage(
            original_content_url = random_image_url,
            preview_image_url = random_image_url
        )
        
        line_bot_api.reply_message(event.reply_token, message)
        
    # 写真という言葉あるとディレクトリから写真がランダムで選ばれて送信されるように
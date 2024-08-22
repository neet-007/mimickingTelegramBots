from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, PicklePersistence, filters
from telegram.ext._contexttypes import ContextTypes
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from os import getenv
from fastapi.responses import JSONResponse
import httpx
load_dotenv()


BOT_API_TOKEN = getenv("BOT_API_TOKEN")
if not BOT_API_TOKEN:
    BOT_API_TOKEN = ""

CHANNEL_ID = getenv("CHANNEL_ID")
WEBHOOK_URL = getenv("WEBHOOK_URL")
    
SERVER_URL = "http://127.0.0.1:5000"

ptb = (
    Application.builder()
    .updater(None)
    .persistence(PicklePersistence("bot_data"))
    .token(BOT_API_TOKEN) 
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    print(WEBHOOK_URL)
    if not WEBHOOK_URL:
        return

    await ptb.bot.setWebhook(WEBHOOK_URL) 
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

@app.post("/verify-user")
async def verify_user(request: Request):
    print("reseved update")
    req = await request.json()
    try:
        err = req["err"]
        data = req["data"]
        chat_id = req["chat_id"]
    except KeyError:
        print("key error")
        return

    print("Sending message")
    if err:
        try:
            text = f"error happend {err}\n"
            await ptb.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"Error sending message: {e}")
            raise HTTPException(status_code=500, detail="Failed to send message")
    else:
        try:
            if isinstance(data, list):
                data = "\n".join(data)

            text = f"success {data}"
            await ptb.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"Error sending message: {e}")
            raise HTTPException(status_code=500, detail="Failed to send message")

    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

async def start(update: Update , _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not update.message:
        return

    await update.message.reply_text("starting...")


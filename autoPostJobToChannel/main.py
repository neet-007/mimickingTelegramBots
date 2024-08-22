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

@app.post("/jobs")
async def get_jobs(request: Request):
    print("reseved update")
    req = await request.json()
    try:
        chat_id = req["message"]["to_user"]
        text = req["message"]["text"]
    except KeyError:
        print("key error")
        return

    print("Sending message")
    try:
        await ptb.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

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

async def start_verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or not isinstance(context.user_data, dict):
        return

    try:
        print(context.bot_data["verified_users"])
        verified_users = context.bot_data["verified_users"]
    except KeyError:
        verified_users = None


    if verified_users and update.effective_chat.id in verified_users:
        await update.message.reply_text("you are already verified")
        return ConversationHandler.END

    await update.message.reply_text("now send your phone number")
    return 1

async def verify_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or not isinstance(context.user_data, dict):
        return

    phone_number = update.message.text

    await update.message.reply_text("proccissing your phone number...")
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id":update.effective_chat.id,
            "phone_number":phone_number
        }
        response = await client.post(SERVER_URL + '/verify-phone-number', json=payload)
        json_data = response.json()
        err = json_data["err"]
        data = json_data["data"]
        if err:
            await update.message.reply_text(f"error {data}")
            return 1
        else:
            context.user_data["phone_number"] = phone_number
            await update.message.reply_text("send your birth day")
            return 2

async def verify_birth_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or not isinstance(context.user_data, dict):
        return

    try:
        phone_number = context.user_data["phone_number"]
    except KeyError:
        await update.message.reply_text("and eeror happend please try again")
        return ConversationHandler.END

    birthday = update.message.text

    await update.message.reply_text("proccissing your birth day...")
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id":update.effective_chat.id,
            "birth_day":birthday,
            "phone_number":phone_number
        }
        response = await client.post(SERVER_URL + "/verify-birth-day", json=payload)
        json_data = response.json()
        err = json_data["err"]
        data = json_data["data"]
        if err:
            context.user_data.clear()
            await update.message.reply_text(f"error {data}")
            return 2
        else:
            context.user_data.clear()
            try:
                verified_users = context.bot_data["verified_users"]
                if not isinstance(verified_users, set):
                    verified_users = set()
            except KeyError:
                verified_users = set()

            verified_users.add(update.effective_chat.id)
            context.bot_data["verified_users"] = verified_users
            await update.message.reply_text("you will recive jobs now")
            return ConversationHandler.END

async def cancel_verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or not isinstance(context.user_data, dict):
        return

    await update.message.reply_text("canceld")
    return ConversationHandler.END

ptb.add_handler(CommandHandler("start", start))
conversaion_hanlder = ConversationHandler(entry_points=[CommandHandler("verify", start_verify_user)],
                                          states={
                                                1:[MessageHandler((filters.TEXT & ~ filters.COMMAND), verify_phone_number)],
                                                2:[MessageHandler((filters.TEXT & ~ filters.COMMAND), verify_birth_day)]
                                          },
                                          fallbacks=[CommandHandler("cancel", cancel_verify_user)])
ptb.add_handler(conversaion_hanlder)








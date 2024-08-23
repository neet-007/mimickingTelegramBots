from contextlib import asynccontextmanager
from http import HTTPStatus
from quart import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, PicklePersistence, filters
from telegram.ext._contexttypes import ContextTypes
from fastapi import FastAPI, Request, Response, HTTPException, responses
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
ADMIN_ID = getenv("ADMIN_CHAT_ID")   
SERVER_URL = getenv("SERVER_URL")

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

@app.post("/admin/view-keys")
async def admin_view_keys(request: Request):
    print("reseved update")
    if not ADMIN_ID:
        return

    print("dejosing")
    response_json = await request.json()
    print("json ready")
    try:
        err = response_json["err"]
        data = response_json["data"]
    except KeyError:
        return await ptb.bot.send_message(text="error happend response data is not formatted correctly", chat_id=ADMIN_ID)
    try:
        message_id = response_json["message_id"]
    except KeyError:
        message_id = None
    print(message_id)
    key = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="prev page", callback_data="admin-view-keys-prev"),
            InlineKeyboardButton(text="next page", callback_data="admin-view-keys-next"),
            InlineKeyboardButton(text="end", callback_data="admin-view-keys-end"),
        ]])

    if err:
        await ptb.bot.send_message(text=f"an error happend {err}", chat_id=ADMIN_ID)
    if message_id:
        print("sending message")
        await ptb.bot.send_message(text=f"here are the next/prev games\n{data}", chat_id=ADMIN_ID, reply_markup=key)
    else:
        await ptb.bot.send_message(text=f"the available keys\n{data}", chat_id=ADMIN_ID, reply_markup=key)

    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

@app.post("/admin/add-keys")
async def admin_add_keys(request: Request):
    print("reseved update")
    if not ADMIN_ID:
        return

    print("dejosing")
    response_json = await request.json()
    print("json ready")
    try:
        err = response_json["err"]
    except KeyError:
        return await ptb.bot.send_message(text="error happend response data is not formatted correctly", chat_id=ADMIN_ID)
    if err:
        await ptb.bot.send_message(text=f"an error happend {err}", chat_id=ADMIN_ID)

    await ptb.bot.send_message(text="key added succefully", chat_id=ADMIN_ID)
    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

async def handle_start_admin_view_keys(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return

    print(ADMIN_ID)
    print(update.effective_user.id)
    if update.effective_user.id != int(ADMIN_ID):
        return await update.message.reply_text("you are not verfied for this")

    context.user_data["state"] = "view-games"
    context.user_data["page"] = 0
    await update.message.reply_text(text="send the games you want to see if you want to send all games reply with 'all' ")

async def handle_admin_view_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return

    if update.effective_user.id != int(ADMIN_ID):
        return await update.message.reply_text("you are not verfied for this")

    games = "&games=".join([game.strip() for game in update.message.text.lower().split(",")])

    context.user_data["games"] = games
    async with httpx.AsyncClient() as client:
        await client.get(url=SERVER_URL + f"/admin/view-keys?games={games}&page=0")

async def handle_start_admin_add_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return

    if update.effective_user.id != int(ADMIN_ID):
        return await update.message.reply_text("you are not verfied for this")
    
    await update.message.reply_text("send the game and key separated by comma 'game, key' ")

async def handle_admin_add_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return

    if update.effective_user.id != int(ADMIN_ID):
        return await update.message.reply_text("you are not verfied for this")
    
    text = update.message.text.lower().split(",")
    if len(text) != 2:
        return await update.message.reply_text("please send game then key separated by comm")

    async with httpx.AsyncClient() as client:
        await client.post(url=SERVER_URL + f"/admin/add-keys", json={
                "chat_id":ADMIN_ID,
                "game":text[0].strip(),
                "key":text[1].strip()
        })

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_user or not isinstance(context.user_data, dict) or not update.effective_chat or not SERVER_URL:
        return

    q = update.callback_query
    await q.answer()
    
    if not q.data:
        return

    print("call back")
    if "admin" in q.data:
        if not ADMIN_ID or update.effective_user.id != int(ADMIN_ID):
            return await context.bot.send_message(text="this is only for admins", chat_id=update.effective_chat.id)

    if q.data == "admin-view-keys-prev":
        try:
            page = max(context.user_data["page"] - 1, 0)
            print(page)
            games = context.user_data["games"]
        except KeyError:
            return await context.bot.send_message(text="an error happend try again", chat_id=update.effective_chat.id)

        async with httpx.AsyncClient() as client:
            context.user_data["page"] = page
            print(f"sending to user page {page}")
            url = SERVER_URL + f"/admin/view-keys?games={games}&page={page}&message_id={q.message.message_id}"
            await client.get(url=url)
            await q.edit_message_text("proccissing")
            print("sent")
    if q.data == "admin-view-keys-next":
        try:
            page = context.user_data["page"] + 1
            print(page)
            games = context.user_data["games"]
        except KeyError:
            return await context.bot.send_message(text="an error happend try again", chat_id=update.effective_chat.id)

        async with httpx.AsyncClient() as client:
            context.user_data["page"] = page
            print(f"sending to user page {page}")
            url = SERVER_URL + f"/admin/view-keys?games={games}&page={page}&message_id={q.message.message_id}"
            await client.get(url=url)
            await q.edit_message_text("proccissing")
            print("sent")
    if q.data == "admin-view-keys-end":
        pass

async def start(update: Update , _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not update.message:
        return

    await update.message.reply_text("starting...")

ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CommandHandler("admin_view_keys", handle_start_admin_view_keys))
ptb.add_handler(CommandHandler("admin_add_keys", handle_start_admin_add_keys))
#ptb.add_handler(MessageHandler((filters.TEXT & ~ filters.COMMAND), handle_admin_view_keys))
ptb.add_handler(MessageHandler((filters.TEXT & ~ filters.COMMAND), handle_admin_add_keys))
ptb.add_handler(CallbackQueryHandler(handle_callbacks))




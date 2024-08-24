from contextlib import asynccontextmanager
from http import HTTPStatus
from quart import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import telegram
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

VIEW_KEYS, ADD_KEYS, DELETE_KEYS, MODIFY_KEYS, VIEW_GAMES, BUY_GAMES  = range(6)
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

@app.post("/admin/modify-keys")
async def admin_modify_keys(request: Request):
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

@app.post("/admin/delete-keys")
async def admin_delete_keys(request: Request):
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

@app.post("/view-keys")
async def view_keys(request: Request):
    print("reseved update")

    print("dejosing")
    response_json = await request.json()
    print("json ready")
    try:
        err = response_json["err"]
        data = response_json["data"]
        chat_id = response_json["chat_id"]
    except KeyError:
        return await ptb.bot.send_message(text="error happend response data is not formatted correctly", chat_id=chat_id)
    try:
        message_id = response_json["message_id"]
    except KeyError:
        message_id = None
    print(message_id)
    key = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="prev page", callback_data="view-keys-prev"),
            InlineKeyboardButton(text="next page", callback_data="view-keys-next"),
            InlineKeyboardButton(text="end", callback_data="view-keys-end"),
        ]])

    if err:
        await ptb.bot.send_message(text=f"an error happend {err}", chat_id=chat_id)
    if message_id:
        print("sending message")
        await ptb.bot.send_message(text=f"here are the next/prev games\n{data}", chat_id=chat_id, reply_markup=key)
    else:
        await ptb.bot.send_message(text=f"the available keys\n{data}", chat_id=chat_id, reply_markup=key)

    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

@app.post("/buy-games")
async def buy_games(request: Request):
    print("reseved update")
    print("dejosing")

    response_json = await request.json()
    print("json ready")
    try:
        err = response_json["err"]
        chat_id = response_json["chat_id"]
        data = response_json["data"]
    except KeyError:
        return await ptb.bot.send_message(text="error happend response data is not formatted correctly", chat_id=chat_id)
    if err:
        await ptb.bot.send_message(text=f"an error happend {err}", chat_id=chat_id)
    if data:
        await ptb.bot.send_message(text=f"game bought succesfuly\n{data}", chat_id=chat_id)
    return JSONResponse(content={"status": "success", "message": "Message sent successfully"}, status_code=200)

async def handle_start_admin_view_keys(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    print(ADMIN_ID)
    print(update.effective_user.id)
    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END

    context.user_data["state"] = "view-games"
    context.user_data["page"] = 0
    await update.message.reply_text(text="send the games you want to see if you want to send all games reply with 'all' ")
    return VIEW_KEYS

async def handle_admin_view_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END

    games = "&games=".join([game.strip() for game in update.message.text.lower().split(",")])

    context.user_data["games"] = games
    async with httpx.AsyncClient() as client:
        await client.get(url=SERVER_URL + f"/admin/view-keys?games={games}&page=0")

    return ConversationHandler.END

async def handle_start_admin_add_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    await update.message.reply_text("send the game and key separated by comma 'game, key' ")
    return ADD_KEYS

async def handle_admin_add_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    text = update.message.text.split(",")
    if len(text) != 2:
        return await update.message.reply_text("please send game then key separated by comm")

    async with httpx.AsyncClient() as client:
        await client.post(url=SERVER_URL + f"/admin/add-keys", json={
                "chat_id":ADMIN_ID,
                "game":text[0].strip().lower(),
                "key":text[1].strip()
        })

    return ConversationHandler.END

async def handle_start_admin_modify_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    await update.message.reply_text("send the game and the old key and new key separated by comma 'game, key' ")
    return MODIFY_KEYS

async def handle_admin_modify_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    text = update.message.text.split(",")
    if len(text) != 3:
        await update.message.reply_text("please send game then old key then new key separated by comm")
        return MODIFY_KEYS

    async with httpx.AsyncClient() as client:
        await client.put(url=SERVER_URL + f"/admin/modify-keys", json={
                "chat_id":ADMIN_ID,
                "game":text[0].strip().lower(),
                "old_key":text[1].strip(),
                "new_key":text[2].strip()
        })

    return ConversationHandler.END

async def handle_start_admin_delete_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    await update.message.reply_text("send the game and key separated by comma 'game, key' ")
    return DELETE_KEYS

async def handle_admin_delete_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not ADMIN_ID or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    if update.effective_user.id != int(ADMIN_ID):
        await update.message.reply_text("you are not verfied for this")
        return ConversationHandler.END
    
    text = update.message.text.split(",")
    if len(text) != 2:
        await update.message.reply_text("please send game then key separated by comm")
        return DELETE_KEYS

    async with httpx.AsyncClient() as client:
        await client.delete(url=SERVER_URL + f"/admin/delete-keys?game={text[0].lower()}&key={text[1].strip()}&chat_id={ADMIN_ID}")
    
    return ConversationHandler.END

async def handle_start_view_keys(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    context.user_data["state"] = "view-games"
    context.user_data["page"] = 0
    await update.message.reply_text(text="send the games you want to see if you want to send all games reply with 'all' ")
    return VIEW_GAMES

async def handle_view_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    games = "&games=".join([game.strip() for game in update.message.text.lower().split(",")])

    context.user_data["games"] = games
    context.user_data["chat_id"] = update.effective_chat.id
    async with httpx.AsyncClient() as client:
        await client.get(url=SERVER_URL + f"/view-keys?games={games}&page=0&chat_id={update.effective_chat.id}")
    
    return ConversationHandler.END

async def handle_start_buy_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    await update.message.reply_text("send the game you want then the number of copies separated by comma ','")
    return BUY_GAMES

async def handle_buy_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not SERVER_URL or not isinstance(context.user_data, dict):
        return ConversationHandler.END

    text = update.message.text.split(",")
    if len(text) != 2:
        await update.message.reply_text("please send game then old key then new key separated by comm")
        return BUY_GAMES

    async with httpx.AsyncClient() as client:
        await client.post(url=SERVER_URL + f"/buy-games", json={
                "chat_id":ADMIN_ID,
                "game":text[0].strip().lower(),
                "count":text[1].strip(),
        })

    return ConversationHandler.END

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_user or not isinstance(context.user_data, dict) or not update.effective_chat or not SERVER_URL:
        return

    q = update.callback_query
    await q.answer()
    
    if not q.data:
        return

    admin = False
    print("call back")
    if "admin" in q.data:
        admin = True
        if not ADMIN_ID or update.effective_user.id != int(ADMIN_ID):
            return await context.bot.send_message(text="this is only for admins", chat_id=update.effective_chat.id)

    data = q.data.replace("admin-", "")
    if data == "view-keys-prev":
        try:
            page = max(context.user_data["page"] - 1, 0)
            print(page)
            games = context.user_data["games"]
        except KeyError:
            return await context.bot.send_message(text="an error happend try again", chat_id=update.effective_chat.id)

        async with httpx.AsyncClient() as client:
            context.user_data["page"] = page
            print(f"sending to user page {page}")
            if admin:
                url = SERVER_URL + f"/admin/view-keys?games={games}&page={page}&message_id={q.message.message_id}"
            else:
                chat_id = context.user_data["chat_id"]
                url = SERVER_URL + f"/view-keys?games={games}&page={page}&message_id={q.message.message_id}&chat_id={chat_id}"
            await client.get(url=url)
            await q.edit_message_text("proccissing")
            print("sent")
    if data == "view-keys-next":
        try:
            page = context.user_data["page"] + 1
            print(page)
            games = context.user_data["games"]
        except KeyError:
            return await context.bot.send_message(text="an error happend try again", chat_id=update.effective_chat.id)

        async with httpx.AsyncClient() as client:
            context.user_data["page"] = page
            print(f"sending to user page {page}")
            if admin:
                url = SERVER_URL + f"/admin/view-keys?games={games}&page={page}&message_id={q.message.message_id}"
            else:
                chat_id = context.user_data["chat_id"]
                url = SERVER_URL + f"/view-keys?games={games}&page={page}&message_id={q.message.message_id}&chat_id={chat_id}"
            await client.get(url=url)
            await q.edit_message_text("proccissing")
            print("sent")
    if data == "view-keys-end":
        pass

async def start(update: Update , _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not update.message:
        return

    await update.message.reply_text("starting...")

view_keys_conv = ConversationHandler(
    entry_points=[CommandHandler("admin_view_keys", handle_start_admin_view_keys)],
    states={VIEW_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_view_keys)]},
    fallbacks=[],
)

add_keys_conv = ConversationHandler(
    entry_points=[CommandHandler("admin_add_keys", handle_start_admin_add_keys)],
    states={ADD_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_add_keys)]},
    fallbacks=[],
)

delete_keys_conv = ConversationHandler(
    entry_points=[CommandHandler("admin_delete_keys", handle_start_admin_delete_keys)],
    states={DELETE_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_delete_keys)]},
    fallbacks=[],
)

modify_keys_conv = ConversationHandler(
    entry_points=[CommandHandler("admin_modify_keys", handle_start_admin_modify_keys)],
    states={MODIFY_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_modify_keys)]},
    fallbacks=[],
)

view_games_conv = ConversationHandler(
    entry_points=[CommandHandler("view_games", handle_start_view_keys)],
    states={VIEW_GAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_view_keys)]},
    fallbacks=[],
)

buy_games_conv = ConversationHandler(
    entry_points=[CommandHandler("buy_games", handle_start_buy_keys)],
    states={BUY_GAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buy_keys)]},
    fallbacks=[],
)

ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(view_keys_conv)
ptb.add_handler(add_keys_conv)
ptb.add_handler(delete_keys_conv)
ptb.add_handler(modify_keys_conv)
ptb.add_handler(view_games_conv)
ptb.add_handler(buy_games_conv)
ptb.add_handler(CallbackQueryHandler(handle_callbacks))




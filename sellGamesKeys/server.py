from dotenv import load_dotenv
from os import getenv
import json as js
from quart import Quart, json, request, jsonify
import httpx

load_dotenv()


app = Quart(__name__)

async def send_request(webhook_url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)
        print(response)

@app.route("/", methods=["GET"])
def index():
    return "hello"

@app.route("/admin/view-keys", methods=["GET"])
async def admin_view_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/view-keys"

    data = await request.json
    chat_id = data.get("chat_id")
    games = request.args.getlist("games")

    try:
        with open("./database.json") as f:
            file = json.load(f)
            text = ""
            if len(games) > 0:
                for game in games:
                    price = file[game]
                    keys = "\n".join(file[game]["keys"])
                    text += f"{game}:{price}\n\n{keys}"

                    payload = {
                        "chat_id":chat_id,
                        "err":None,
                        "data":text
                    }

                    await send_request(webhook_url, payload)

                    return jsonify(payload), 200
            else:
                for game, details in file.items():
                    price = details["price"]
                    keys = "\n".join(details["keys"])
                    text += f"{game}:{price}\n\n{keys}"

                payload = {
                    "chat_id":chat_id,
                    "err":None,
                    "data":text
                }

                await send_request(webhook_url, payload)

                return jsonify(payload), 200
    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

    return ""

@app.route("/admin/add-keys", methods=["POST"])
async def admin_add_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/add-keys"

    data = await request.json
    chat_id = data.get("chat_id")
    game = data.get("game")
    key = data.get("key")

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            if not game in file:
                return jsonify({"err": "game does not exist"}), 404

            file[game]["keys"].append(key)

            f.seek(0)
            json.dump(file, f)
            f.truncate()

            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":None
            }

            await send_request(webhook_url, payload)
            return jsonify(payload), 200

    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/admin/modify-keys", methods=["POST"])
async def admin_modify_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/modify-keys"

    data = await request.json
    chat_id = data.get("chat_id")
    game = data.get("game")
    key = data.get("old_key")
    new_key = data.get("new_key")

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            if not game in file:
                return jsonify({"err": "game does not exist"}), 404

            keys = file[game]["keys"]
            try:
                keys[keys.index(key)] = new_key
            except ValueError:
                return jsonify({"err": "key does not exist"}), 404

            f.seek(0)
            json.dump(file, f)
            f.truncate()

            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":None
            }

            await send_request(webhook_url, payload)
            return jsonify(payload), 200

    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/admin/delte-keys", methods=["POST"])
async def admin_delete_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/modify-keys"

    data = await request.json
    chat_id = data.get("chat_id")
    game = data.get("game")
    key = data.get("key")

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            if not game in file:
                return jsonify({"err": "game does not exist"}), 404

            keys = file[game]["keys"]
            try:
                keys.remove(key)
            except ValueError:
                return jsonify({"err": "key does not exist"}), 404

            f.seek(0)
            json.dump(file, f)
            f.truncate()

            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":None
            }

            await send_request(webhook_url, payload)
            return jsonify(payload), 200

    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/buy-game", methods=["POST"])
async def buy_game():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/buy-game"

    data = await request.json
    chat_id = data.get("chat_id")
    game = data.get("game")
    count = data.get("count")
    bought_keys = [0] * count

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            if not game in file:
                return jsonify({"err": "game does not exist"}), 404

            keys = file[game]["keys"]
            price = file[game]["price"]

            len_keys = len(keys)
            for i in range(count):
                if len_keys <= 0:
                    break
                bought_keys[i] = keys.pop()
                len_keys -= 1

            f.seek(0)
            json.dump(file, f)
            f.truncate()

            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":{
                    "gane":game,
                    "keys":bought_keys,
                    "bill":len(bought_keys) * price,
                    "remaining_keys":count
                }
            }

            await send_request(webhook_url, payload)
            return jsonify(payload), 200

    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/view-keys", methods=["GET"])
async def view_games():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/view-keys"

    data = await request.json
    chat_id = data.get("chat_id")
    page = request.args.get("page")
    if not page:
        page = 1

    skip = int(page) * 20

    try:
        with open("./database.json") as f:
            file = json.load(f)
            text = ""
            for game, details in file.items():
                if skip > 0:
                    skip -= 1
                    continue
                price = details["price"]
                text += f"{game}:{price}, available:{len(details["keys"])}"

            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":text
            }

            await send_request(webhook_url, payload)

            return jsonify(payload), 200
    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

if __name__ == "__main__":
    app.run(debug=True)

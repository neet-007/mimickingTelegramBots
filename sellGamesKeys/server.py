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

    chat_id = request.args.get("chat_id")
    games = request.args.getlist("games")
    page = request.args.get("page")
    message_id = request.args.get("message_id")
    if not page:
        page = 0

    count = 20
    skip = int(page) * count

    print(games)
    print("openaing file")
    try:
        with open("./database.json") as f:
            print("file opend")
            file = json.load(f)
            text = ""
            if len(games) > 1:
                for game in games:
                    if skip > 0:
                        skip -= 1
                        continue
                    if count <= 0:
                        break
                    price = file[game]["price"]
                    keys = "\n".join(file[game]["keys"])
                    text += f"{game}:{price}\n\n{keys}\n\n"

                print(text)
                text += f"{int(page) + 1}"
                payload = {
                    "chat_id":chat_id,
                    "err":None,
                    "data":text,
                    "message_id":message_id
                }

                await send_request(webhook_url, payload)

                return jsonify(payload), 200
            else:
                print("one game pr all")
                for game, details in file.items():
                    if skip > 0:
                        skip -= 1
                        continue
                    if count <= 0:
                        break
                    price = details["price"]
                    keys = "\n".join(details["keys"])
                    text += f"{game}:{price}\n\n{keys}\n\n"
                    count -= 1

                text += f"{int(page) + 1}"
                payload = {
                    "chat_id":chat_id,
                    "err":None,
                    "data":text,
                    "message_id":message_id
                }

                print("sending request")
                await send_request(webhook_url, payload)

                return jsonify(payload), 200
    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/admin/add-keys", methods=["POST"])
async def admin_add_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/add-keys"

    data = await request.json
    print(type(data))
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

@app.route("/admin/modify-keys", methods=["PUT"])
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
            print(keys)
            print(new_key)
            print(keys.index(key))
            try:
                keys[keys.index(key)] = new_key
            except ValueError:
                return jsonify({"err": "key does not exist"}), 404

            print(keys)
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

@app.route("/admin/delete-keys", methods=["DELETE"])
async def admin_delete_keys():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/admin/delete-keys"

    print("here")
    chat_id = request.args.get("chat_id")
    game = request.args.get("game")
    key = request.args.get("key")

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            print(game)
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

            print("sending reqiest")
            await send_request(webhook_url, payload)
            return jsonify(payload), 200

    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

@app.route("/buy-games", methods=["POST"])
async def buy_game():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "/buy-games"

    data = await request.json
    chat_id = data.get("chat_id")
    game = data.get("game")
    count = int(data.get("count"))
    bought_keys = [""] * count

    try:
        with open("./database.json", "r+") as f:
            file = json.load(f)
            if not game in file:
                return jsonify({"err": "game does not exist"}), 404

            keys = file[game]["keys"]
            price = file[game]["price"]

            len_keys = len(keys)
            if len_keys == 0:
                payload = {
                    "chat_id":chat_id,
                    "err":"all games are sold",
                    "data":None
                }

                await send_request(webhook_url, payload)
                return jsonify(payload), 400

            for i in range(count):
                if len_keys <= 0:
                    break
                bought_keys[i] = str(keys.pop()) + "\n"
                len_keys -= 1
                count -= 1

            f.seek(0)
            json.dump(file, f)
            f.truncate()

            keys = "\n".join(bought_keys)
            payload = {
                "chat_id":chat_id,
                "err":None,
                "data":f"game:{game}\nbill:{len(bought_keys) * price}\nremaining keys:{count}\nkeys:{keys}\n"
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

    webhook_url += "/view-keys"

    chat_id = request.args.get("chat_id")
    games = request.args.getlist("games")
    page = request.args.get("page")
    message_id = request.args.get("message_id")
    if not page:
        page = 0

    count = 20
    skip = int(page) * count

    try:
        with open("./database.json") as f:
            print("file opend")
            file = json.load(f)
            text = ""
            if len(games) > 1:
                for game in games:
                    if skip > 0:
                        skip -= 1
                        continue
                    if count <= 0:
                        break
                    price = file[game]["price"]
                    text += f"{game}:{price}\n"

                print(text)
                text += f"{int(page) + 1}"
                payload = {
                    "chat_id":chat_id,
                    "err":None,
                    "data":text,
                    "message_id":message_id
                }

                await send_request(webhook_url, payload)

                return jsonify(payload), 200
            else:
                print("one game pr all")
                for game, details in file.items():
                    if skip > 0:
                        skip -= 1
                        continue
                    if count <= 0:
                        break
                    price = details["price"]
                    text += f"{game}:{price}\n"
                    count -= 1

                text += f"{int(page) + 1}"
                payload = {
                    "chat_id":chat_id,
                    "err":None,
                    "data":text,
                    "message_id":message_id
                }

                print("sending request")
                await send_request(webhook_url, payload)

                return jsonify(payload), 200
    except OSError:
        return jsonify({"err": "could not open file"}), 500
    except js.JSONDecodeError:
        return jsonify({"err": "file is not valid JSON"}), 500

if __name__ == "__main__":
    app.run(debug=True)

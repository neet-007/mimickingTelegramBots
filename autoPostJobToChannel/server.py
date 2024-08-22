from dotenv import load_dotenv
from os import getenv
from quart import Quart, request, jsonify
import httpx

load_dotenv()


app = Quart(__name__)

jobs = {
  "web": [
    {
      "company": "Tech Innovators",
      "salary": "$70,000",
      "role": "Frontend Developer",
      "experience_level": "Mid-Level"
    },
    {
      "company": "Code Masters",
      "salary": "$85,000",
      "role": "Full Stack Developer",
      "experience_level": "Senior-Level"
    }
  ],
  "cooking": [
    {
      "company": "Gourmet Delights",
      "salary": "$45,000",
      "role": "Sous Chef",
      "experience_level": "Mid-Level"
    },
    {
      "company": "Culinary Creations",
      "salary": "$30,000",
      "role": "Line Cook",
      "experience_level": "Entry-Level"
    }
  ],
  "driving": [
    {
      "company": "Fast Logistics",
      "salary": "$50,000",
      "role": "Truck Driver",
      "experience_level": "Mid-Level"
    },
    {
      "company": "City Transport",
      "salary": "$35,000",
      "role": "Taxi Driver",
      "experience_level": "Entry-Level"
    }
  ],
  "accounting": [
    {
      "company": "Finance Pros",
      "salary": "$60,000",
      "role": "Accountant",
      "experience_level": "Mid-Level"
    },
    {
      "company": "Numbers & Co.",
      "salary": "$90,000",
      "role": "Senior Financial Analyst",
      "experience_level": "Senior-Level"
    }
  ],
  "manager": [
    {
      "company": "Global Enterprises",
      "salary": "$120,000",
      "role": "Operations Manager",
      "experience_level": "Senior-Level"
    },
    {
      "company": "Retail Giants",
      "salary": "$80,000",
      "role": "Store Manager",
      "experience_level": "Mid-Level"
    }
  ],
  "cop": [
    {
      "company": "City Police Department",
      "salary": "$55,000",
      "role": "Police Officer",
      "experience_level": "Entry-Level"
    },
    {
      "company": "Metro Police",
      "salary": "$70,000",
      "role": "Detective",
      "experience_level": "Mid-Level"
    }
  ]
}

users = {
    "050 123 4567": {
        "bd": "13/9/2002",
        "pf": ["web", "cooking"]
    },
    "055 987 6543": {
        "bd": "4/3/1998",
        "pf": ["driving", "accounting"]
    },
    "053 234 5678": {
        "bd": "25/6/2003",
        "pf": ["web", "cooking"]
    },
    "059 876 5432": {
        "bd": "13/11/1985",
        "pf": ["manager", "cop"]
    },
    "050 112 3344": {
        "bd": "15/7/1990",
        "pf": ["programming", "web"]
    },
    "052 998 7766": {
        "bd": "22/12/1992",
        "pf": ["manager", "accounting"]
    },
    "054 556 7788": {
        "bd": "9/4/1988",
        "pf": ["driving", "cop"]
    },
    "056 345 6789": {
        "bd": "2/5/2000",
        "pf": ["cooking", "web"]
    },
    "057 123 9876": {
        "bd": "18/11/1983",
        "pf": ["manager", "programming"]
    },
    "058 234 5567": {
        "bd": "29/8/1995",
        "pf": ["cop", "driving"]
    },
    "059 112 3344": {
        "bd": "10/1/1987",
        "pf": ["accounting", "cooking"]
    },
    "051 223 3445": {
        "bd": "30/6/1994",
        "pf": ["web", "programming"]
    },
    "050 445 6677": {
        "bd": "14/9/1999",
        "pf": ["driving", "manager"]
    },
    "053 556 8899": {
        "bd": "21/3/2001",
        "pf": ["cooking", "accounting"]
    },
    "052 778 9900": {
        "bd": "6/2/1989",
        "pf": ["cop", "web"]
    },
    "054 889 0011": {
        "bd": "12/7/1997",
        "pf": ["manager", "driving"]
    },
}

users_phone_number_to_chat_id = {
    "050 123 4567": "1619288289",
    "055 987 6543": "7320680699",
    "053 234 5678": "1619288289",
    "059 876 5432": "7320680699",
    "050 112 3344": "1619288289",
    "052 998 7766": "7320680699",
    "054 556 7788": "1619288289",
    "056 345 6789": "7320680699",
    "057 123 9876": "1619288289",
    "058 234 5567": "7320680699",
    "059 112 3344": "1619288289",
    "051 223 3445": "7320680699",
    "050 445 6677": "1619288289",
    "053 556 8899": "7320680699",
    "052 778 9900": "1619288289",
    "054 889 0011": "7320680699",
}

async def send_request(webhook_url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)
        print(response)

@app.route("/", methods=["GET"])
def index():
    return "hello"

@app.route("/get-jobs", methods=["POST"])
async def get_jobs():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "jobs"

    data = await request.json
    chat_id = data.get("chat_id")

    phone_number = data.get("phone_number")
    if not phone_number:
        payload_ = {
            "err": "No phone number provided",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 400

    if phone_number not in users:
        payload_ = {
            "err": "User does not exist",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 404

    user = users[phone_number]
    data = ""
    for category in jobs:
        if category in user["pf"]:
            data += f"{category}\n".capitalize()
            for job in jobs[category]:
                for key, val in job.items():
                    data += f"{key}:{val}\n".capitalize()
                data += "\n"

            data += "\n"
    payload_ = {
        "err": None,
        "data": data,
        "chat_id": chat_id
    }

    await send_request(webhook_url, payload_)
    return jsonify(payload_), 200

@app.route("/verify-phone-number", methods=["POST"])
async def verify_phone_number():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "verify-user"

    data = await request.json
    chat_id = data.get("chat_id")

    phone_number = data.get("phone_number")
    if not phone_number:
        payload_ = {
            "err": "No phone number provided",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 400

    if phone_number not in users:
        payload_ = {
            "err": "User does not exist",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 404

    payload_ = {
        "err": None,
        "data": None,
        "chat_id": chat_id
    }

    await send_request(webhook_url, payload_)
    return jsonify(payload_), 200

@app.route("/verify-birth-day", methods=["POST"])
async def verify_birth_day():
    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return jsonify({"error": "No webhook URL configured"}), 500

    webhook_url += "verify-user"

    data = await request.json
    chat_id = data.get("chat_id")

    phone_number = data.get("phone_number")
    birth_day = data.get("birth_day")
    if not phone_number or not birth_day:
        payload_ = {
            "err": "No phone number or birthday provided",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 400

    user = users.get(phone_number)
    if not user:
        payload_ = {
            "err": "User does not exist",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 404

    if user["bd"] != birth_day:
        payload_ = {
            "err": "Wrong birthday",
            "data": None,
            "chat_id": chat_id
        }
        await send_request(webhook_url, payload_)
        return jsonify(payload_), 400

    payload_ = {
        "err": None,
        "chat_id": chat_id,
        "data": user["pf"]
    }

    await send_request(webhook_url, payload_)
    return jsonify(payload_), 200

@app.route("/add-jobs", methods=["POST"])
async def add_jobs():
    data = await request.json

    category = data["category"]
    job = {
        "company":data["company"],
        "salary":data["salary"],
          "role": data["role"],
          "experience_level": data["experience_level"]
    }

    jobs[category].append(job)

    webhook_url = getenv("WEBHOOK_URL")
    if not webhook_url:
        return ""

    webhook_url += "jobs/broadcast"
    print(webhook_url)
    for user in users:
        print("loob userser")
        if category in users[user]["pf"]:
            text = ""
            for key, val in job.items():
                text += f"{key}:{val}\n"

            chat_id = users_phone_number_to_chat_id[user]
            print(chat_id)
            payload_ = {
                "err":None,
                "chat_id":chat_id,
                "data":text
            }

            await send_request(webhook_url, payload_)

    return ""

if __name__ == "__main__":
    app.run(debug=True)

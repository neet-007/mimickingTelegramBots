from dotenv import load_dotenv
from os import getenv
from quart import Quart, request, jsonify
import httpx

load_dotenv()


app = Quart(__name__)


payload = {
    "update_id": 10000,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "John",
            "username": "john_doe",
            "language_code": "en"
        },
        "chat": {
            "id": 123456789,
            "first_name": "John",
            "username": "john_doe",
            "type": "private"
        },
        "date": 1609459200,
        "text": ""
    }
}

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
    "050 123 4567":{
        "bd":"13/9/2002",
        "pf":["web", "cooking"]
    },
    "055 987 6543":{
        "bd":"4/3/1998",
        "pf":["driving", "accounting"]
    },
    "053 234 5678":{
        "bd":"25/6/2003",
        "pf":["web", "cooking"]
    },
    "059 876 5432":{
        "bd":"13/11/1985",
        "pf":["manager", "cop"]
    },
}

users_phone_number_to_chat_id = {
    "050 123 4567":"1619288289",
    "055 987 6543":"1619288289",
    "053 234 5678":"1619288289",
    "059 876 5432":"1619288289"
}

@app.route("/", methods=["GET"])
def index():
    return "hello"

@app.route("/get-jobs", methods=["POST"])
def get_jobs():
    return ""

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

    webhook_url += "jobs"
    print(webhook_url)
    for user in users:
        print("loob userser")
        if category in users[user]["pf"]:
            text = ""
            for key, val in job.items():
                text += f"{key}:{val}\n"

            
            payload_ = payload.copy()
            payload_["message"]["text"] = text
            payload_["message"]["to_user"] = users_phone_number_to_chat_id[user]

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
                print(response)

    return ""

if __name__ == "__main__":
    app.run(debug=True)

#!/bin/python3

#Run this _after_ Open WebUI is finished starting

import requests
import json
import secrets

def create_admin_account(email, password):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "name": "admin",
        "email": email,
        "password": password,
        "profile_image_url": "/user.png"
    }
    json_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/v1/auths/signup", headers=headers, data=json_data)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code == 200:    
        return json_response["token"]
    else:
        print("Admin account already created, trying login...")
        return login_as_admin(email, password)

def login_as_admin(email, password):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "password": password
    }
    json_data = json.dumps(data)

    response = requests.post("http://localhost:8080/api/v1/auths/signin", headers=headers, data=json_data)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code == 200:    
        return json_response["token"]
    else:
        print(json_response)
        error = ""
        if "msg" in json_response:
            error = json_response["msg"]
        elif "detail" in json_response:
            error = json_response["detail"]
        print(f"Failed to login to admin account, error message: {error}")
        return None

def create_expoitable_function(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    function_id = "test_action"
    function_name = "Test Action"
    data = {
        "id": f"{function_id}",
        "name": f"{function_name}",
        "content": ("from pydantic import BaseModel\n"
                    "import sqlite3\n"
                    "from typing import Optional, Union, Generator, Iterator\n"
                    "class Action:\n"
                    "    class Valves(BaseModel):\n"
                    "        pass\n"
                    "    def __init__(self):\n"
                    "        self.valves = self.Valves()\n"
                    "    async def action(\n"
                    "        self,\n"
                    "        body: dict,\n"
                    "        __user__=None,\n"
                    "        __event_emitter__=None,\n"
                    "        __event_call__=None,\n"
                    "    ) -> Optional[dict]:\n"
                    "        connection = sqlite3.connect('/app/backend/data/webui.db')\n"
                    "        cursor = connection.cursor()\n"
                    "        cursor.execute('SELECT user_id from chat LIMIT 1')\n"
                    "        first_chat = cursor.fetchone()\n"
                    "        message = f'Testing Open WebUI action function. Example data: {first_chat}'\n"
                    "        connection.close()\n"
                    "        response = await __event_call__(\n"
                    "            {\n"
                    "                'type': 'status',\n"
                    "                'data': {\n"
                    "                    'description': f'{message}',\n"
                    "                    'done': True\n"
                    "                },\n"
                    "            }\n"
                    "        )"),
        "meta": {
            "description": "Testing Open WebUI's action function.",
            "manifest": {}
        }
    }

    json_data = json.dumps(data)
    #Send request to create the function
    response = requests.post("http://localhost:8080/api/v1/functions/create", headers=headers, data=json_data)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code != 200:
        if "msg" in json_response:
            error = json_response["msg"]
        elif "detail" in json_response:
            error = json_response["detail"]
        print(f"Failed to create action function, error message: {error}")
        return None
    #Send request to enable the function
    response = requests.post(f"http://localhost:8080/api/v1/functions/id/{function_id}/toggle", headers=headers)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code != 200:
        if "msg" in json_response:
            error = json_response["msg"]
        elif "detail" in json_response:
            error = json_response["detail"]
        print(f"Failed to toggle action function, error message: {error}")
        return None
    #Send request to make the function visible to all users
    response = requests.post(f"http://localhost:8080/api/v1/functions/id/{function_id}/toggle/global", headers=headers)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code != 200:
        if "msg" in json_response:
            error = json_response["msg"]
        elif "detail" in json_response:
            error = json_response["detail"]
        print(f"Failed to globally toggle action function, error message: {error}")
        return None

def enable_signups(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "SHOW_ADMIN_DETAILS": False,
        "WEBUI_URL": "http://localhost:3000",
        "ENABLE_SIGNUP": True,
        "ENABLE_API_KEY": True,
        "ENABLE_API_KEY_ENDPOINT_RESTRICTIONS": False,
        "API_KEY_ALLOWED_ENDPOINTS": "",
        "ENABLE_CHANNELS": False,
        "DEFAULT_USER_ROLE": "user",
        "JWT_EXPIRES_IN": "-1",
        "ENABLE_COMMUNITY_SHARING": True,
        "ENABLE_MESSAGE_RATING": True
    }
    json_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/v1/auths/admin/config", headers=headers, data=json_data)
    response_str = response.content.decode("utf-8")
    json_response = json.loads(response_str)
    if response.status_code != 200:
        print(f"Failed to enable signups, error message: {json_response['msg']}")
        return None

email = "admin@example.com"
password = secrets.token_urlsafe(32)
auth_token = create_admin_account(email, password)
create_expoitable_function(auth_token)
enable_signups(auth_token)
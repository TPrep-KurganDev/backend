#Надо запустить main.py перед запуском теста

from typing import Any

import requests

BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_PATH = "/auth/login"
REGISTER_PATH = "/auth/register"
CREATE_EXAM_PATH = "/exams/"

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "testAdmin"

def register_user(email: str, password: str, admin_username: str):
    url = BASE_URL + REGISTER_PATH
    payload = {"email": email, "password": password, "user_name": admin_username}

    try:
        r = requests.post(url, json=payload)
    except requests.RequestException as e:
        print(f"Network error during register: {e}")
        return None

    if r.status_code != 200:
        print(f"Register failed: status={r.status_code}, body={r.text}")
        return None
    print(f"Registered successfully")
    return None

def login_user(email: str, password: str):
    url = BASE_URL + LOGIN_PATH
    payload = {"email": email, "password": password}

    try:
        r = requests.post(url, json=payload)
    except requests.RequestException as e:
        print(f"Network error during login: {e}")
        return None

    if r.status_code != 200:
        print(f"Login failed: status={r.status_code}, body={r.text}")
        return None

    data = r.json()
    value = data.get("access_token")
    id = data.get("id")
    print(f"Login successfully")
    return value if isinstance(value, str) else None

def create_exam(token: str, title: str = "Auto Exam") -> dict[str, Any] | None:
    url = BASE_URL + CREATE_EXAM_PATH

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title}

    try:
        r = requests.post(url, json=payload, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None

    if r.status_code not in (200, 201):
        print(f"Exam creation failed: status={r.status_code}, body={r.text}")
        return None

    print(f"Exam creation successfully")
    data = r.json()
    exam_id = data.get("id")
    return exam_id

def add_card(exam_id: int, token: str):
    url = BASE_URL + f"/exams/{exam_id}/cards"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(url, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    print("Created card successfully")

if __name__ == "__main__":
    register_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin1")
    token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    exam_id = create_exam(token, title="Test Exam")
    add_card(exam_id, token)



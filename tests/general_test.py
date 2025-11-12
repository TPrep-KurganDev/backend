# Надо запустить main.py перед запуском теста

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
        if r.text == '{"error":"UnexceptableStrategy","message":"User already exists"}':
            print("Скорее всего не отчистили users перед стартом теста")
        return None
    print(f"Registered without errors")
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
    print(f"Login without errors")
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

    print(f"Exam creation without errors")
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
    data = r.json()
    print("Created card without errors")
    return data['card_id']


def fill_card(exam_id: int, token: str, card_id: int):
    url = BASE_URL + f"/exams/{exam_id}/cards/{card_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": "Что такое ядро гомоморфизма?",
               "answer": "Ядро гомоморфизма в математике — это множество элементов одной алгебраической структуры (группы, кольца, поля и т. д.), которые при гомоморфизме (отображении, сохраняющем алгебраические операции) отображаются в нулевую подсистему второй структуры."}
    try:
        r = requests.patch(url, json=payload, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    print("Card filled without errors")


def take_session(exam_id: int, token: str):
    url = BASE_URL + f"/session"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"exam_id": exam_id}
    try:
        r = requests.post(url, json=payload, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    data = r.json()
    return data['id'], data['questions']


def get_question(question_id: int):
    url = BASE_URL + f"/cards/{question_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    data = r.json()
    print(data)


def set_answer(session_id: str, question_id: id, flag: bool):
    url = BASE_URL + f"/session/{session_id}/answer"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"question_id": question_id, "value": flag}
    try:
        r = requests.post(url, headers=headers, params=params)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    print(f"Set Answer status={r.status_code}, body={r.text}")


def get_cards(exam_id: int):
    url = BASE_URL + f"/exams/{exam_id}/cards"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
    except requests.RequestException as e:
        print(f"Network error during exam creation: {e}")
        return None
    data = r.json()
    print(data)


if __name__ == "__main__":
    register_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin1")
    token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    exam_id = create_exam(token, title="Test Exam")
    card_id = add_card(exam_id, token)
    fill_card(exam_id, token, card_id)
    for i in range(10):
        card_id = add_card(exam_id, token)
        fill_card(exam_id, token, card_id)

    get_cards(exam_id)

    session_id, questions = take_session(exam_id, token)
    flag = False
    for question_id in questions:
        get_question(question_id)
        set_answer(session_id, question_id, flag)
        flag = not flag

import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_PATH = "/auth/login"
CREATE_EXAM_PATH = "/exams"

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "testAdmin"

def get_access_token(email: str, password: str):
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
    return data.get("access_token")


def create_exam(token: str, title: str = "Auto Exam"):
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

    return r.json()


def main():
    print("Logging in...")
    token = get_access_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("Aborting due to login failure.")
        sys.exit(1)

    print("Login successful. Token:", token)

    print("Creating exam...")
    exam = create_exam(token, title="My Test Exam")
    if exam is None:
        print("Exam creation failed.")
        sys.exit(1)

    print("Exam created successfully:")
    print(exam)


if __name__ == "__main__":
    main()

"""Test data configurations for parametrized tests."""

# User mock data configurations
USERS = {
    "default": {
        "id": 1,
        "email": "test@example.com",
        "user_name": "Test User",
        "password_hash": "hashed_password",
    },
    "user_2": {
        "id": 2,
        "email": "user2@example.com",
        "user_name": "User Two",
        "password_hash": "hashed_password_2",
    },
    "admin": {
        "id": 3,
        "email": "admin@example.com",
        "user_name": "Admin User",
        "password_hash": "admin_hashed_password",
    },
}

# Exam mock data configurations
EXAMS = {
    "default": {
        "id": 1,
        "title": "Mock Exam",
        "creator_id": 1,
    },
    "exam_2": {
        "id": 2,
        "title": "Mock Exam 2",
        "creator_id": 1,
    },
    "empty_exam": {
        "id": 3,
        "title": "Empty Exam",
        "creator_id": 2,
    },
}

# Card mock data configurations
CARDS = {
    "exam_1_cards": [
        {
            "card_id": i,
            "exam_id": 1,
            "question": f"Q{i}?",
            "answer": f"A{i}",
            "number": i,
        }
        for i in range(1, 4)
    ],
    "exam_2_cards": [
        {
            "card_id": i + 10,
            "exam_id": 2,
            "question": f"Question {i}?",
            "answer": f"Answer {i}",
            "number": i,
        }
        for i in range(1, 6)
    ],
}

# Statistic mock data configurations
STATISTICS = {
    "default": {
        "id": 1,
        "user_id": 1,
        "card_id": 1,
        "exam_id": 1,
        "mistakes_count": 5,
    },
    "high_mistakes": {
        "id": 2,
        "user_id": 1,
        "card_id": 2,
        "exam_id": 1,
        "mistakes_count": 15,
    },
    "no_mistakes": {
        "id": 3,
        "user_id": 2,
        "card_id": 1,
        "exam_id": 2,
        "mistakes_count": 0,
    },
}
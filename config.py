"""
설정 파일
"""
import os

# 데이터베이스 설정
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sebang_scm.db")
DB_DIR = os.path.join(os.path.dirname(__file__), "data")

# 역할 정의
ROLES = {
    "발주사": "발주사",
    "주문담당자": "주문담당자",
    "제조담당자": "제조담당자"
}

# 주문 상태
ORDER_STATUS = {
    "대기": "대기",
    "승인": "승인",
    "생산중": "생산중",
    "입고완료": "입고완료",
    "출하완료": "출하완료"
}

# 주문 구분
ORDER_TYPE = {
    "긴급": "긴급",
    "일반": "일반"
}

# 우선순위 범위
PRIORITY_MIN = 1
PRIORITY_MAX = 9
PRIORITY_DEFAULT = 5

# 디자인 색상
COLORS = {
    "primary": "#1E3A5F",
    "secondary": "#4A90E2",
    "accent": "#FF6B35",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545"
}


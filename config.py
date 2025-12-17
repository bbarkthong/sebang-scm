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
    "일반": "일반",
    "긴급": "긴급",
}

# 우선순위 범위
PRIORITY_MIN = 1
PRIORITY_MAX = 9
PRIORITY_DEFAULT = 5

# 디자인 색상 (세방산업 디자인 시스템)
# 레퍼런스 우선순위: 1) gbattery.com, 2) sebangind.com, 3) spc.co.kr
COLORS = {
    "primary": "#003366",      # 세방산업 메인 블루 (프로페셔널, 신뢰감)
    "secondary": "#0066CC",    # 세방산업 서브 블루 (액션, 링크)
    "accent": "#FF6600",       # 강조 색상 (긴급, 중요)
    "success": "#00AA44",      # 성공 (승인, 완료)
    "warning": "#FF9900",      # 경고 (대기, 주의)
    "danger": "#CC0000",       # 위험 (거부, 오류)
    "light_bg": "#F5F7FA",     # 연한 배경
    "border": "#E0E4E8",       # 테두리 색상
    "text_primary": "#1A1A1A", # 주요 텍스트
    "text_secondary": "#666666" # 보조 텍스트
}


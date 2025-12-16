"""
주문 관련 유틸리티 함수
"""
from datetime import datetime
from database.connection import get_db, close_db
from database.models import OrderMaster


def generate_order_no(order_date=None) -> str:
    """
    주문번호 자동 생성
    형식: ORD-YYYY-NNN (예: ORD-2024-001)
    
    Args:
        order_date: 주문일자 (datetime.date 객체), None이면 오늘 날짜 사용
    
    Returns:
        생성된 주문번호 문자열
    """
    if order_date is None:
        order_date = datetime.now().date()
    
    year = order_date.strftime("%Y")
    
    # 해당 연도의 주문 번호 조회
    db = get_db()
    try:
        # 해당 연도로 시작하는 주문번호 찾기
        year_prefix = f"ORD-{year}-"
        existing_orders = db.query(OrderMaster).filter(
            OrderMaster.order_no.like(f"{year_prefix}%")
        ).order_by(OrderMaster.order_no.desc()).all()
        
        # 다음 순번 결정
        if existing_orders:
            # 가장 큰 번호 찾기
            max_num = 0
            for order in existing_orders:
                try:
                    # ORD-YYYY-NNN 형식에서 NNN 추출
                    num_part = order.order_no.split("-")[-1]
                    num = int(num_part)
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
            
            next_num = max_num + 1
        else:
            next_num = 1
        
        # 3자리 숫자로 포맷팅
        order_no = f"{year_prefix}{next_num:03d}"
        
        return order_no
    finally:
        close_db(db)


"""
데이터 검증 유틸리티
"""
from datetime import datetime, date
from decimal import Decimal


def validate_order_no(order_no: str) -> tuple[bool, str]:
    """주문번호 검증"""
    if not order_no or not order_no.strip():
        return False, "주문번호를 입력해주세요."
    if len(order_no) > 50:
        return False, "주문번호는 50자 이하여야 합니다."
    return True, ""


def validate_order_date(order_date: date) -> tuple[bool, str]:
    """주문일자 검증"""
    if not order_date:
        return False, "주문일자를 선택해주세요."
    return True, ""


def validate_order_type(order_type: str) -> tuple[bool, str]:
    """주문구분 검증"""
    if order_type not in ["긴급", "일반"]:
        return False, "주문구분은 '긴급' 또는 '일반'이어야 합니다."
    return True, ""


def validate_customer_company(company: str) -> tuple[bool, str]:
    """고객사 검증"""
    if not company or not company.strip():
        return False, "고객사를 입력해주세요."
    return True, ""


def validate_item_code(item_code: str) -> tuple[bool, str]:
    """품목코드 검증"""
    if not item_code or not item_code.strip():
        return False, "품목코드를 입력해주세요."
    return True, ""


def validate_item_name(item_name: str) -> tuple[bool, str]:
    """품목명 검증"""
    if not item_name or not item_name.strip():
        return False, "품목명을 입력해주세요."
    return True, ""


def validate_qty(qty: int) -> tuple[bool, str]:
    """수량 검증"""
    if qty is None:
        return False, "수량을 입력해주세요."
    if qty <= 0:
        return False, "수량은 0보다 커야 합니다."
    return True, ""


def validate_unit_price(price: Decimal) -> tuple[bool, str]:
    """단가 검증"""
    if price is None:
        return False, "단가를 입력해주세요."
    if price < 0:
        return False, "단가는 0 이상이어야 합니다."
    return True, ""


def validate_priority(priority: int) -> tuple[bool, str]:
    """우선순위 검증"""
    if priority is None:
        return False, "우선순위를 입력해주세요."
    if priority < 1 or priority > 9:
        return False, "우선순위는 1~9 사이의 값이어야 합니다."
    return True, ""


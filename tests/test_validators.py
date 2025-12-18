"""
데이터 검증 유틸리티 테스트
"""
import pytest
import sys
import os
from datetime import date
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import (
    validate_order_no,
    validate_order_date,
    validate_order_type,
    validate_customer_company,
    validate_item_code,
    validate_item_name,
    validate_qty,
    validate_unit_price,
    validate_priority
)


class TestOrderValidation:
    """주문 검증 테스트"""
    
    def test_validate_order_no_valid(self):
        """유효한 주문번호 테스트"""
        is_valid, msg = validate_order_no("ORD-2024-001")
        assert is_valid is True
        assert msg == ""
    
    def test_validate_order_no_empty(self):
        """빈 주문번호 테스트"""
        is_valid, msg = validate_order_no("")
        assert is_valid is False
        assert "주문번호" in msg
    
    def test_validate_order_no_none(self):
        """None 주문번호 테스트"""
        is_valid, msg = validate_order_no(None)
        assert is_valid is False
    
    def test_validate_order_date_valid(self):
        """유효한 주문일자 테스트"""
        is_valid, msg = validate_order_date(date.today())
        assert is_valid is True
    
    def test_validate_order_date_none(self):
        """None 주문일자 테스트"""
        is_valid, msg = validate_order_date(None)
        assert is_valid is False
    
    def test_validate_order_type_valid(self):
        """유효한 주문구분 테스트"""
        is_valid, msg = validate_order_type("긴급")
        assert is_valid is True
        
        is_valid, msg = validate_order_type("일반")
        assert is_valid is True
    
    def test_validate_order_type_invalid(self):
        """잘못된 주문구분 테스트"""
        is_valid, msg = validate_order_type("기타")
        assert is_valid is False
    
    def test_validate_customer_company_valid(self):
        """유효한 고객사 테스트"""
        is_valid, msg = validate_customer_company("삼성SDI")
        assert is_valid is True
    
    def test_validate_customer_company_empty(self):
        """빈 고객사 테스트"""
        is_valid, msg = validate_customer_company("")
        assert is_valid is False


class TestItemValidation:
    """품목 검증 테스트"""
    
    def test_validate_item_code_valid(self):
        """유효한 품목코드 테스트"""
        is_valid, msg = validate_item_code("ITEM001")
        assert is_valid is True
    
    def test_validate_item_code_empty(self):
        """빈 품목코드 테스트"""
        is_valid, msg = validate_item_code("")
        assert is_valid is False
    
    def test_validate_item_name_valid(self):
        """유효한 품목명 테스트"""
        is_valid, msg = validate_item_name("ESS (Energy Storage System)")
        assert is_valid is True
    
    def test_validate_item_name_empty(self):
        """빈 품목명 테스트"""
        is_valid, msg = validate_item_name("")
        assert is_valid is False


class TestQuantityValidation:
    """수량 검증 테스트"""
    
    def test_validate_qty_valid(self):
        """유효한 수량 테스트"""
        is_valid, msg = validate_qty(100)
        assert is_valid is True
    
    def test_validate_qty_zero(self):
        """0 수량 테스트"""
        is_valid, msg = validate_qty(0)
        assert is_valid is False
    
    def test_validate_qty_negative(self):
        """음수 수량 테스트"""
        is_valid, msg = validate_qty(-10)
        assert is_valid is False
    
    def test_validate_qty_none(self):
        """None 수량 테스트"""
        is_valid, msg = validate_qty(None)
        assert is_valid is False


class TestPriceValidation:
    """단가 검증 테스트"""
    
    def test_validate_unit_price_valid(self):
        """유효한 단가 테스트"""
        is_valid, msg = validate_unit_price(Decimal("1000.00"))
        assert is_valid is True
    
    def test_validate_unit_price_zero(self):
        """0 단가 테스트"""
        is_valid, msg = validate_unit_price(Decimal("0"))
        assert is_valid is True  # 0도 유효함
    
    def test_validate_unit_price_negative(self):
        """음수 단가 테스트"""
        is_valid, msg = validate_unit_price(Decimal("-100"))
        assert is_valid is False
    
    def test_validate_unit_price_none(self):
        """None 단가 테스트"""
        is_valid, msg = validate_unit_price(None)
        assert is_valid is False


class TestPriorityValidation:
    """우선순위 검증 테스트"""
    
    def test_validate_priority_valid(self):
        """유효한 우선순위 테스트"""
        for priority in [1, 5, 9]:
            is_valid, msg = validate_priority(priority)
            assert is_valid is True
    
    def test_validate_priority_too_low(self):
        """너무 낮은 우선순위 테스트"""
        is_valid, msg = validate_priority(0)
        assert is_valid is False
    
    def test_validate_priority_too_high(self):
        """너무 높은 우선순위 테스트"""
        is_valid, msg = validate_priority(10)
        assert is_valid is False
    
    def test_validate_priority_none(self):
        """None 우선순위 테스트"""
        is_valid, msg = validate_priority(None)
        assert is_valid is False


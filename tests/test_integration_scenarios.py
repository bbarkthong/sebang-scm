"""
통합 시나리오 테스트 (전체 프로세스)
"""
import pytest
import sys
import os
from datetime import date
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import OrderMaster, OrderDetail, Warehouse, ShippingPlan, User
from auth.auth import hash_password


class TestCompleteOrderFlow:
    """전체 주문 프로세스 통합 테스트"""
    
    def test_complete_order_to_shipping_flow(self, test_db, sample_order_data, sample_order_detail_data):
        """주문 등록부터 출하까지 전체 프로세스 테스트"""
        
        # 1. 사용자 생성 (발주사)
        password_hash = hash_password("test123")
        user = User(
            user_id="test_user_001",
            username="test_customer",
            password_hash=password_hash,
            role="발주사",
            company_name="테스트회사"
        )
        test_db.add(user)
        test_db.flush()
        
        # 2. 주문 등록
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by="test_customer",
            status="대기"
        )
        test_db.add(order_master)
        test_db.flush()
        
        order_detail = OrderDetail(
            order_no=sample_order_detail_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            order_qty=sample_order_detail_data["order_qty"],
            unit_price=Decimal(str(sample_order_detail_data["unit_price"]))
        )
        test_db.add(order_detail)
        test_db.commit()
        
        assert order_master.status == "대기"
        
        # 3. 주문 승인
        order_master.status = "승인"
        order_master.priority = 7
        order_master.approved_by = "order_manager"
        test_db.commit()
        
        approved_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        assert approved_order.status == "승인"
        
        # 4. 생산중 상태 변경
        approved_order.status = "생산중"
        test_db.commit()
        
        # 5. 입고 등록
        warehouse = Warehouse(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            received_qty=100,
            received_date=date.today(),
            received_by="manufacturing"
        )
        test_db.add(warehouse)
        approved_order.status = "입고완료"
        test_db.commit()
        
        assert approved_order.status == "입고완료"
        
        # 6. 출하 계획 수립
        shipping_plan = ShippingPlan(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            planned_shipping_date=date(2024, 12, 31),
            planned_qty=100,
            status="계획",
            created_by="order_manager"
        )
        test_db.add(shipping_plan)
        test_db.commit()
        
        # 7. 출하 완료 처리
        shipping_plan.status = "출하완료"
        order_detail.shipping_qty = shipping_plan.planned_qty
        order_detail.actual_shipping_date = shipping_plan.planned_shipping_date
        order_detail.shipping_amount = float(order_detail.shipping_qty * order_detail.unit_price)
        approved_order.status = "출하완료"
        test_db.commit()
        
        # 최종 검증
        final_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert final_order.status == "출하완료"
        
        final_detail = test_db.query(OrderDetail).filter(
            OrderDetail.order_no == sample_order_data["order_no"]
        ).first()
        
        assert final_detail.shipping_qty == 100
        assert final_detail.actual_shipping_date == date(2024, 12, 31)
        assert final_detail.shipping_amount > 0
        
        completed_plan = test_db.query(ShippingPlan).filter(
            ShippingPlan.order_no == sample_order_data["order_no"]
        ).first()
        
        assert completed_plan.status == "출하완료"


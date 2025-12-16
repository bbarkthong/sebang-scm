"""
출하 계획 시나리오 테스트
"""
import pytest
import sys
import os
from datetime import date
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import OrderMaster, OrderDetail, Warehouse, ShippingPlan


class TestShippingPlanning:
    """출하 계획 시나리오 테스트"""
    
    def test_create_shipping_plan(self, test_db, sample_order_data, sample_order_detail_data):
        """출하 계획 생성 테스트"""
        # 입고 완료된 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="입고완료"
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
        
        # 입고 등록
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
        test_db.commit()
        
        # 출하 계획 생성
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
        
        # 검증
        saved_plan = test_db.query(ShippingPlan).filter(
            ShippingPlan.order_no == sample_order_data["order_no"]
        ).first()
        
        assert saved_plan is not None
        assert saved_plan.planned_qty == 100
        assert saved_plan.status == "계획"
        assert saved_plan.created_by == "order_manager"
    
    def test_complete_shipping(self, test_db, sample_order_data, sample_order_detail_data):
        """출하 완료 처리 테스트"""
        # 입고 완료된 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="입고완료"
        )
        test_db.add(order_master)
        test_db.flush()
        
        order_detail = OrderDetail(
            order_no=sample_order_detail_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            order_qty=100,
            unit_price=Decimal(str(sample_order_detail_data["unit_price"]))
        )
        test_db.add(order_detail)
        test_db.commit()
        
        # 출하 계획 생성
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
        
        # 출하 완료 처리
        shipping_plan.status = "출하완료"
        order_detail.shipping_qty = shipping_plan.planned_qty
        order_detail.actual_shipping_date = shipping_plan.planned_shipping_date
        order_detail.shipping_amount = float(order_detail.shipping_qty * order_detail.unit_price)
        test_db.commit()
        
        # 검증
        completed_plan = test_db.query(ShippingPlan).filter(
            ShippingPlan.order_no == sample_order_data["order_no"]
        ).first()
        
        assert completed_plan.status == "출하완료"
        
        updated_detail = test_db.query(OrderDetail).filter(
            OrderDetail.order_no == sample_order_data["order_no"]
        ).first()
        
        assert updated_detail.shipping_qty == 100
        assert updated_detail.actual_shipping_date == date(2024, 12, 31)
        assert updated_detail.shipping_amount == float(100 * Decimal(str(sample_order_detail_data["unit_price"])))
    
    def test_partial_shipping(self, test_db, sample_order_data, sample_order_detail_data):
        """부분 출하 테스트"""
        # 입고 완료된 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="입고완료"
        )
        test_db.add(order_master)
        test_db.flush()
        
        order_detail = OrderDetail(
            order_no=sample_order_detail_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            order_qty=200,  # 주문 수량 200
            unit_price=Decimal(str(sample_order_detail_data["unit_price"]))
        )
        test_db.add(order_detail)
        test_db.commit()
        
        # 입고 등록 (200개)
        warehouse = Warehouse(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            received_qty=200,
            received_date=date.today(),
            received_by="manufacturing"
        )
        test_db.add(warehouse)
        test_db.commit()
        
        # 부분 출하 계획 (100개만)
        shipping_plan1 = ShippingPlan(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            planned_shipping_date=date(2024, 12, 31),
            planned_qty=100,
            status="계획",
            created_by="order_manager"
        )
        test_db.add(shipping_plan1)
        test_db.commit()
        
        # 검증
        plans = test_db.query(ShippingPlan).filter(
            ShippingPlan.order_no == sample_order_data["order_no"],
            ShippingPlan.order_seq == sample_order_detail_data["order_seq"]
        ).all()
        
        assert len(plans) == 1
        assert plans[0].planned_qty == 100
        
        # 나머지 출하 계획 추가
        shipping_plan2 = ShippingPlan(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            planned_shipping_date=date(2025, 1, 15),
            planned_qty=100,
            status="계획",
            created_by="order_manager"
        )
        test_db.add(shipping_plan2)
        test_db.commit()
        
        # 총 출하 계획 수량 확인
        all_plans = test_db.query(ShippingPlan).filter(
            ShippingPlan.order_no == sample_order_data["order_no"],
            ShippingPlan.order_seq == sample_order_detail_data["order_seq"]
        ).all()
        
        total_planned = sum(p.planned_qty for p in all_plans)
        assert total_planned == 200


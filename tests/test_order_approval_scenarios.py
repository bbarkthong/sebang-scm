"""
주문 승인 시나리오 테스트
"""
import pytest
import sys
import os
from datetime import date, datetime
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import OrderMaster, OrderDetail


class TestOrderApproval:
    """주문 승인 시나리오 테스트"""
    
    def test_approve_order(self, test_db, sample_order_data, sample_order_detail_data):
        """주문 승인 테스트"""
        # 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="대기"
        )
        test_db.add(order_master)
        test_db.commit()
        
        # 주문 승인
        order_master.status = "승인"
        order_master.priority = 7
        order_master.approved_by = "order_manager"
        order_master.approved_at = datetime.now()
        test_db.commit()
        
        # 검증
        approved_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert approved_order.status == "승인"
        assert approved_order.priority == 7
        assert approved_order.approved_by == "order_manager"
        assert approved_order.approved_at is not None
    
    def test_reject_order(self, test_db, sample_order_data):
        """주문 거부 테스트"""
        # 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="대기"
        )
        test_db.add(order_master)
        test_db.commit()
        
        # 주문 거부
        order_master.status = "거부"
        test_db.commit()
        
        # 검증
        rejected_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert rejected_order.status == "거부"
    
    def test_set_priority_levels(self, test_db, sample_order_data):
        """우선순위 설정 테스트"""
        # 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="대기"
        )
        test_db.add(order_master)
        test_db.commit()
        
        # 다양한 우선순위 테스트
        for priority in [1, 5, 9]:
            order_master.priority = priority
            test_db.commit()
            
            updated_order = test_db.query(OrderMaster).filter(
                OrderMaster.order_no == sample_order_data["order_no"]
            ).first()
            
            assert updated_order.priority == priority
    
    def test_change_status_to_production(self, test_db, sample_order_data):
        """생산중 상태 변경 테스트"""
        # 승인된 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="승인"
        )
        test_db.add(order_master)
        test_db.commit()
        
        # 생산중으로 상태 변경
        order_master.status = "생산중"
        test_db.commit()
        
        # 검증
        updated_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert updated_order.status == "생산중"


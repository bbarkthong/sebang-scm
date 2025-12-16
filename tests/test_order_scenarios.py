"""
주문 등록 시나리오 테스트
"""
import pytest
import sys
import os
from datetime import date
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import OrderMaster, OrderDetail, User


class TestOrderRegistration:
    """주문 등록 시나리오 테스트"""
    
    def test_create_order_with_details(self, test_db, sample_order_data, sample_order_detail_data):
        """주문 마스터와 상세를 함께 생성하는 테스트"""
        # 주문 마스터 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"]
        )
        test_db.add(order_master)
        test_db.flush()
        
        # 주문 상세 생성
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
        
        # 검증
        saved_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert saved_order is not None
        assert saved_order.order_no == sample_order_data["order_no"]
        assert saved_order.status == "대기"
        assert saved_order.priority == 5  # 기본값
        
        saved_detail = test_db.query(OrderDetail).filter(
            OrderDetail.order_no == sample_order_data["order_no"]
        ).first()
        
        assert saved_detail is not None
        assert saved_detail.item_code == sample_order_detail_data["item_code"]
        assert saved_detail.order_qty == sample_order_detail_data["order_qty"]
    
    def test_order_master_default_values(self, test_db, sample_order_data):
        """주문 마스터 기본값 테스트"""
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"]
        )
        test_db.add(order_master)
        test_db.commit()
        
        assert order_master.status == "대기"
        assert order_master.priority == 5
        assert order_master.created_at is not None
    
    def test_multiple_order_details(self, test_db, sample_order_data):
        """여러 주문 상세 항목 테스트"""
        # 주문 마스터 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"]
        )
        test_db.add(order_master)
        test_db.flush()
        
        # 여러 주문 상세 생성
        details = [
            {"seq": 1, "item_code": "ITEM001", "item_name": "품목1", "qty": 100, "price": 1000},
            {"seq": 2, "item_code": "ITEM002", "item_name": "품목2", "qty": 200, "price": 2000},
            {"seq": 3, "item_code": "ITEM003", "item_name": "품목3", "qty": 300, "price": 3000},
        ]
        
        for detail in details:
            order_detail = OrderDetail(
                order_no=sample_order_data["order_no"],
                order_seq=detail["seq"],
                item_code=detail["item_code"],
                item_name=detail["item_name"],
                order_qty=detail["qty"],
                unit_price=Decimal(str(detail["price"]))
            )
            test_db.add(order_detail)
        
        test_db.commit()
        
        # 검증
        saved_details = test_db.query(OrderDetail).filter(
            OrderDetail.order_no == sample_order_data["order_no"]
        ).order_by(OrderDetail.order_seq).all()
        
        assert len(saved_details) == 3
        assert saved_details[0].order_seq == 1
        assert saved_details[1].order_seq == 2
        assert saved_details[2].order_seq == 3
    
    def test_order_relationship(self, test_db, sample_order_data, sample_order_detail_data):
        """주문 마스터와 상세 간 관계 테스트"""
        # 주문 마스터 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"]
        )
        test_db.add(order_master)
        test_db.flush()
        
        # 주문 상세 생성
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
        
        # 관계 검증
        saved_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert len(saved_order.details) == 1
        assert saved_order.details[0].item_code == sample_order_detail_data["item_code"]
        
        assert order_detail.master.order_no == sample_order_data["order_no"]


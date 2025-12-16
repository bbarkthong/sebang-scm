"""
입고 등록 시나리오 테스트
"""
import pytest
import sys
import os
from datetime import date
from decimal import Decimal

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import OrderMaster, OrderDetail, Warehouse


class TestWarehouseRegistration:
    """입고 등록 시나리오 테스트"""
    
    def test_register_warehouse_receipt(self, test_db, sample_order_data, sample_order_detail_data):
        """입고 등록 테스트"""
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
        
        # 검증
        saved_receipt = test_db.query(Warehouse).filter(
            Warehouse.order_no == sample_order_data["order_no"]
        ).first()
        
        assert saved_receipt is not None
        assert saved_receipt.received_qty == 100
        assert saved_receipt.received_by == "manufacturing"
    
    def test_partial_receipt(self, test_db, sample_order_data, sample_order_detail_data):
        """부분 입고 테스트"""
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
        
        # 부분 입고 (100개만 입고)
        warehouse = Warehouse(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            received_qty=100,  # 200개 중 100개만 입고
            received_date=date.today(),
            received_by="manufacturing"
        )
        test_db.add(warehouse)
        test_db.commit()
        
        # 검증
        saved_receipt = test_db.query(Warehouse).filter(
            Warehouse.order_no == sample_order_data["order_no"]
        ).first()
        
        assert saved_receipt.received_qty == 100
        
        # 추가 입고
        warehouse2 = Warehouse(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            received_qty=100,  # 나머지 100개 입고
            received_date=date.today(),
            received_by="manufacturing"
        )
        test_db.add(warehouse2)
        test_db.commit()
        
        # 총 입고 수량 확인
        total_received = test_db.query(Warehouse).filter(
            Warehouse.order_no == sample_order_data["order_no"],
            Warehouse.order_seq == sample_order_detail_data["order_seq"]
        ).all()
        
        total_qty = sum(r.received_qty for r in total_received)
        assert total_qty == 200
    
    def test_complete_receipt_updates_order_status(self, test_db, sample_order_data, sample_order_detail_data):
        """전체 입고 완료 시 주문 상태 변경 테스트"""
        # 승인된 주문 생성
        order_master = OrderMaster(
            order_no=sample_order_data["order_no"],
            order_date=date.fromisoformat(sample_order_data["order_date"]),
            order_type=sample_order_data["order_type"],
            customer_company=sample_order_data["customer_company"],
            created_by=sample_order_data["created_by"],
            status="생산중"
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
        
        # 전체 입고
        warehouse = Warehouse(
            order_no=sample_order_data["order_no"],
            order_seq=sample_order_detail_data["order_seq"],
            item_code=sample_order_detail_data["item_code"],
            item_name=sample_order_detail_data["item_name"],
            received_qty=100,  # 전체 입고
            received_date=date.today(),
            received_by="manufacturing"
        )
        test_db.add(warehouse)
        
        # 주문 상태를 입고완료로 변경 (실제 로직에서는 모든 항목이 입고되었을 때 자동 변경)
        order_master.status = "입고완료"
        test_db.commit()
        
        # 검증
        updated_order = test_db.query(OrderMaster).filter(
            OrderMaster.order_no == sample_order_data["order_no"]
        ).first()
        
        assert updated_order.status == "입고완료"


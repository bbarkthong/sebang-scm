import pytest
from datetime import date
from services.order_service import create_order
from services.approval_service import approve_order
from services.warehousing_service import register_receipts
from database.models import OrderMaster, Warehouse

class TestWarehouseRegistration:
    """입고 등록 시나리오 테스트 (서비스 사용)"""

    @pytest.fixture
    def approved_order(self, test_db):
        """테스트를 위한 승인된 주문 생성"""
        user_info = {"username": "test_placer"}
        order_data = {
            "order_date": date(2024, 1, 15),
            "order_type": "일반",
            "customer_company": "테스트회사"
        }
        details_data = [
            {"item_code": "ITEM001", "item_name": "테스트 품목 1", "order_qty": 100, "unit_price": 1000, "planned_shipping_date": date(2024, 1, 31)},
            {"item_code": "ITEM002", "item_name": "테스트 품목 2", "order_qty": 200, "unit_price": 2000, "planned_shipping_date": date(2024, 1, 31)}
        ]
        
        order_no = create_order(test_db, user_info, order_data, details_data)
        order = test_db.query(OrderMaster).filter_by(order_no=order_no).first()
        approve_order(test_db, order, priority=5, username="manager")
        return order

    def test_register_warehouse_receipt(self, test_db, approved_order):
        """입고 등록 서비스 테스트"""
        receipt_items = [{
            "order_no": approved_order.order_no, "order_seq": 1, "item_code": "ITEM001", "item_name": "테스트 품목 1",
            "received_qty": 100, "received_date": date.today()
        }]
        
        register_receipts(test_db, approved_order, receipt_items, "manufacturer")
        
        saved_receipt = test_db.query(Warehouse).filter_by(order_no=approved_order.order_no, order_seq=1).first()
        
        assert saved_receipt is not None
        assert saved_receipt.received_qty == 100
        assert saved_receipt.received_by == "manufacturer"
        
        # Status should change to 'In Production'
        updated_order = test_db.query(OrderMaster).filter_by(order_no=approved_order.order_no).first()
        assert updated_order.status == "생산중"

    def test_partial_receipt(self, test_db, approved_order):
        """부분 입고 서비스 테스트"""
        # First partial receipt
        receipts1 = [{"order_no": approved_order.order_no, "order_seq": 2, "item_code": "ITEM002", "item_name": "테스트 품목 2", "received_qty": 50, "received_date": date.today()}]
        register_receipts(test_db, approved_order, receipts1, "manufacturer")

        total_received = sum(r.received_qty for r in test_db.query(Warehouse).filter_by(order_no=approved_order.order_no, order_seq=2).all())
        assert total_received == 50
        
        # Second partial receipt
        receipts2 = [{"order_no": approved_order.order_no, "order_seq": 2, "item_code": "ITEM002", "item_name": "테스트 품목 2", "received_qty": 150, "received_date": date.today()}]
        register_receipts(test_db, approved_order, receipts2, "manufacturer")

        total_received = sum(r.received_qty for r in test_db.query(Warehouse).filter_by(order_no=approved_order.order_no, order_seq=2).all())
        assert total_received == 200

    def test_complete_receipt_updates_order_status(self, test_db, approved_order):
        """전체 입고 완료 시 주문 상태 '입고완료' 변경 테스트"""
        receipts = [
            {"order_no": approved_order.order_no, "order_seq": 1, "item_code": "ITEM001", "item_name": "테스트 품목 1", "received_qty": 100, "received_date": date.today()},
            {"order_no": approved_order.order_no, "order_seq": 2, "item_code": "ITEM002", "item_name": "테스트 품목 2", "received_qty": 200, "received_date": date.today()}
        ]
        
        register_receipts(test_db, approved_order, receipts, "manufacturer")
        
        updated_order = test_db.query(OrderMaster).filter_by(order_no=approved_order.order_no).first()
        assert updated_order.status == "입고완료"
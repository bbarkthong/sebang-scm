import pytest
from datetime import date
from services.order_service import create_order
from services.approval_service import approve_order, reject_order, set_order_in_production
from database.models import OrderMaster

class TestOrderApproval:
    """주문 승인 시나리오 테스트 (서비스 사용)"""

    @pytest.fixture(autouse=True)
    def setup_order(self, test_db):
        """테스트를 위한 기본 주문을 생성하는 fixture"""
        self.user_info = {"username": "test_approver"}
        order_data = {
            "order_date": date(2024, 1, 15),
            "order_type": "일반",
            "customer_company": "테스트회사"
        }
        details_data = [{
            "item_code": "ITEM001", "item_name": "테스트 품목", "order_qty": 100,
            "unit_price": 1000.00, "planned_shipping_date": date(2024, 1, 31)
        }]
        
        self.order_no = create_order(test_db, self.user_info, order_data, details_data)
        self.order = test_db.query(OrderMaster).filter_by(order_no=self.order_no).first()

    def test_approve_order(self, test_db):
        """주문 승인 서비스 테스트"""
        approve_order(test_db, self.order, priority=7, username="order_manager")
        
        approved_order = test_db.query(OrderMaster).filter_by(order_no=self.order_no).first()
        
        assert approved_order.status == "승인"
        assert approved_order.priority == 7
        assert approved_order.approved_by == "order_manager"
        assert approved_order.approved_at is not None

    def test_reject_order(self, test_db):
        """주문 거부 서비스 테스트"""
        reject_order(test_db, self.order)
        
        rejected_order = test_db.query(OrderMaster).filter_by(order_no=self.order_no).first()
        assert rejected_order.status == "거부"

    def test_change_status_to_production(self, test_db):
        """생산중 상태 변경 서비스 테스트"""
        # First, approve the order
        approve_order(test_db, self.order, priority=5, username="manager")
        
        # Then, set to production
        set_order_in_production(test_db, self.order)
        
        updated_order = test_db.query(OrderMaster).filter_by(order_no=self.order_no).first()
        assert updated_order.status == "생산중"
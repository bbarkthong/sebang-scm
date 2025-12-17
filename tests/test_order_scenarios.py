import pytest
from datetime import date
from services.order_service import create_order
from database.models import OrderMaster, OrderDetail

class TestOrderRegistration:
    """주문 등록 시나리오 테스트 (서비스 사용)"""
    
    def test_create_order_with_details(self, test_db, sample_user_data):
        """create_order 서비스를 사용하여 주문을 생성하는 테스트"""
        
        user_info = {"username": sample_user_data["username"]}
        order_data = {
            "order_date": date(2024, 1, 15),
            "order_type": "일반",
            "customer_company": "테스트회사"
        }
        details_data = [
            {
                "item_code": "ITEM001",
                "item_name": "테스트 품목",
                "order_qty": 100,
                "unit_price": 1000.00,
                "planned_shipping_date": date(2024, 1, 31)
            }
        ]
        
        order_no = create_order(test_db, user_info, order_data, details_data)
        
        assert order_no is not None
        
        # 검증
        saved_order = test_db.query(OrderMaster).filter(OrderMaster.order_no == order_no).first()
        
        assert saved_order is not None
        assert saved_order.order_no == order_no
        assert saved_order.status == "대기"
        assert saved_order.priority == 5  # 기본값
        assert saved_order.created_by == user_info["username"]
        
        saved_detail = test_db.query(OrderDetail).filter(OrderDetail.order_no == order_no).first()
        
        assert saved_detail is not None
        assert saved_detail.item_code == "ITEM001"
        assert saved_detail.order_qty == 100

    def test_multiple_order_details(self, test_db, sample_user_data):
        """여러 주문 상세 항목과 함께 주문 생성 테스트"""
        user_info = {"username": sample_user_data["username"]}
        order_data = {
            "order_date": date(2024, 1, 15),
            "order_type": "일반",
            "customer_company": "테스트회사"
        }
        details_data = [
            {"item_code": "ITEM001", "item_name": "품목1", "order_qty": 100, "unit_price": 1000, "planned_shipping_date": date(2024, 1, 31)},
            {"item_code": "ITEM002", "item_name": "품목2", "order_qty": 200, "unit_price": 2000, "planned_shipping_date": date(2024, 1, 31)},
            {"item_code": "ITEM003", "item_name": "품목3", "order_qty": 300, "unit_price": 3000, "planned_shipping_date": date(2024, 1, 31)},
        ]
        
        order_no = create_order(test_db, user_info, order_data, details_data)
        
        # 검증
        saved_details = test_db.query(OrderDetail).filter(
            OrderDetail.order_no == order_no
        ).order_by(OrderDetail.order_seq).all()
        
        assert len(saved_details) == 3
        assert saved_details[0].order_seq == 1
        assert saved_details[1].item_name == "품목2"
        assert saved_details[2].order_qty == 300
        
        saved_master = test_db.query(OrderMaster).filter(OrderMaster.order_no == order_no).first()
        assert len(saved_master.details) == 3
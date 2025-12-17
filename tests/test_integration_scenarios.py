import pytest
from datetime import date
from database.models import OrderMaster, OrderDetail, ShippingPlan, User
from auth.auth import hash_password

# Import all necessary services
from services.order_service import create_order
from services.approval_service import approve_order
from services.warehousing_service import register_receipts
from services.shipping_service import create_shipping_plans, instruct_shipping_plans
from services.shipping_registration_service import confirm_shipment_received

class TestCompleteOrderFlow:
    """전체 주문 프로세스 통합 테스트 (서비스 계층 사용)"""
    
    @pytest.fixture
    def setup_users(self, test_db):
        """테스트에 필요한 다양한 역할의 사용자 생성"""
        users = {
            "client": {"username": "test_client", "role": "발주사", "company_name": "테스트회사"},
            "manager": {"username": "test_manager", "role": "주문담당자"},
            "manufacturer": {"username": "test_manufacturer", "role": "제조담당자"}
        }
        for key, user_data in users.items():
            user = User(
                user_id=f"{key}_001",
                username=user_data["username"],
                password_hash=hash_password("test123"),
                role=user_data["role"],
                company_name=user_data.get("company_name")
            )
            test_db.add(user)
        test_db.commit()
        return users

    def test_complete_order_to_shipping_flow(self, test_db, setup_users):
        """주문 등록부터 출하까지 전체 서비스 플로우 테스트"""
        
        # 1. 주문 등록 (by 발주사)
        order_details_data = [{
            "item_code": "ITEM_INTEG_001", "item_name": "통합테스트품목", "order_qty": 100,
            "unit_price": 1500.00, "planned_shipping_date": date(2024, 12, 31)
        }]
        order_data = {
            "order_date": date.today(),
            "order_type": "일반",
            "customer_company": setup_users["client"]["company_name"]
        }
        
        order_no = create_order(test_db, setup_users["client"], order_data, order_details_data)
        
        order = test_db.query(OrderMaster).filter_by(order_no=order_no).first()
        assert order.status == "대기"

        # 2. 주문 승인 (by 주문담당자)
        approve_order(test_db, order, priority=7, username=setup_users["manager"]["username"])
        assert order.status == "승인"
        
        # 3. 입고 등록 (by 제조담당자)
        receipt_items = [{"order_no": order_no, "order_seq": 1, **order_details_data[0]}]
        register_receipts(test_db, order, receipt_items, setup_users["manufacturer"]["username"])
        assert order.status == "입고완료"
        
        # 4. 출하 계획 수립 (by 주문담당자)
        shipping_plan_items = [{
            "order_no": order_no, "order_seq": 1, "planned_qty": 100, "planned_date": date(2024, 12, 31)
        }]
        create_shipping_plans(test_db, shipping_plan_items, setup_users["manager"]["username"])
        
        plan = test_db.query(ShippingPlan).filter_by(order_no=order_no).first()
        assert plan.status == "계획"
        
        # 5. 출하 지시 (by 주문담당자)
        instruct_shipping_plans(test_db, [plan])
        assert plan.status == "지시"
        
        # 6. 출하 완료 (수신 확인, by 발주사)
        detail = test_db.query(OrderDetail).filter_by(order_no=order_no, order_seq=1).first()
        received_items = [{"plan": plan, "detail": detail, "received_qty": 100, "received_date": date.today()}]
        confirm_shipment_received(test_db, order, received_items)
        
        # 최종 검증
        final_order = test_db.query(OrderMaster).filter_by(order_no=order_no).first()
        assert final_order.status == "출하완료"
        
        final_detail = test_db.query(OrderDetail).filter_by(order_no=order_no, order_seq=1).first()
        assert final_detail.shipping_qty == 100
        
        final_plan = test_db.query(ShippingPlan).get(plan.plan_id)
        assert final_plan.status == "출하완료"
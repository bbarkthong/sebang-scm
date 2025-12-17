import pytest
from datetime import date
from services.order_service import create_order
from services.approval_service import approve_order
from services.warehousing_service import register_receipts
from services.shipping_service import create_shipping_plans
from services.shipping_registration_service import confirm_shipment_received
from database.models import OrderMaster, OrderDetail, ShippingPlan

class TestShippingScenarios:
    """출하 관련 시나리오 테스트 (서비스 사용)"""

    @pytest.fixture
    def warehoused_order(self, test_db):
        """테스트를 위한 입고완료된 주문 생성"""
        # 1. Create Order
        order_no = create_order(
            db=test_db,
            user={"username": "test_client"},
            order_data={"order_date": date(2024, 1, 15), "order_type": "일반", "customer_company": "테스트회사"},
            details=[
                {"item_code": "ITEM001", "item_name": "테스트 품목", "order_qty": 200, "unit_price": 1000, "planned_shipping_date": date(2024, 1, 31)}
            ]
        )
        order = test_db.query(OrderMaster).filter_by(order_no=order_no).first()
        
        # 2. Approve Order
        approve_order(test_db, order, priority=5, username="manager")

        # 3. Register Receipt
        register_receipts(
            db=test_db,
            order=order,
            receipt_items=[{
                "order_no": order.order_no, "order_seq": 1, "item_code": "ITEM001", "item_name": "테스트 품목",
                "received_qty": 200, "received_date": date.today()
            }],
            username="manufacturer"
        )
        return test_db.query(OrderMaster).filter_by(order_no=order_no).first()

    def test_create_shipping_plan(self, test_db, warehoused_order):
        """출하 계획 생성 서비스 테스트"""
        shipping_items = [{
            "order_no": warehoused_order.order_no,
            "order_seq": 1,
            "planned_qty": 150,
            "planned_date": date(2024, 12, 31)
        }]
        
        create_shipping_plans(test_db, shipping_items, "shipping_manager")
        
        saved_plan = test_db.query(ShippingPlan).filter_by(order_no=warehoused_order.order_no).first()
        assert saved_plan is not None
        assert saved_plan.planned_qty == 150
        assert saved_plan.status == "계획"

    def test_confirm_shipment_received(self, test_db, warehoused_order):
        """출하 완료 (수신 확인) 서비스 테스트"""
        # 1. Create a plan
        plan_items = [{"order_no": warehoused_order.order_no, "order_seq": 1, "planned_qty": 200, "planned_date": date(2024, 12, 31)}]
        create_shipping_plans(test_db, plan_items, "shipping_manager")
        
        # 2. Instruct the plan (logic is in shipping_service, but we'll simulate it here)
        plan = test_db.query(ShippingPlan).filter_by(order_no=warehoused_order.order_no).first()
        plan.status = "지시"
        test_db.commit()

        # 3. Confirm receipt
        detail = warehoused_order.details[0]
        received_items = [{
            "plan": plan, "detail": detail,
            "received_qty": 200, "received_date": date.today()
        }]
        confirm_shipment_received(test_db, warehoused_order, received_items)

        # Assertions
        updated_plan = test_db.query(ShippingPlan).get(plan.plan_id)
        assert updated_plan.status == "출하완료"
        
        updated_detail = test_db.query(OrderDetail).get((detail.order_no, detail.order_seq))
        assert updated_detail.shipping_qty == 200
        
        # Because the full amount was shipped, the order status should be "출하완료"
        updated_order = test_db.query(OrderMaster).filter_by(order_no=warehoused_order.order_no).first()
        assert updated_order.status == "출하완료"
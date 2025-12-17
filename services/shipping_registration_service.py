
from datetime import date
from decimal import Decimal
from database.models import OrderMaster, OrderDetail, ShippingPlan

def get_orders_for_registration(db, customer_company):
    """
    Fetches orders for a specific customer that have items with 'Instructed' status,
    making them ready for shipping registration.
    """
    # Find all distinct order numbers that have at least one plan with '지시' status
    instructed_order_nos = db.query(ShippingPlan.order_no).filter(
        ShippingPlan.status == "지시"
    ).distinct().all()
    
    order_nos = [no[0] for no in instructed_order_nos]

    if not order_nos:
        return []

    # Fetch the actual order objects for that customer
    return db.query(OrderMaster).filter(
        OrderMaster.customer_company == customer_company,
        OrderMaster.order_no.in_(order_nos)
    ).order_by(OrderMaster.order_date.desc()).all()

def get_plans_for_registration(db, order_no):
    """
    Fetches the specific shipping plan items for an order that are in 'Instructed' status.
    """
    return db.query(ShippingPlan).filter_by(order_no=order_no, status="지시").all()

def confirm_shipment_received(db, order, received_items):
    """
    Updates the status of shipping plans and order details upon client confirmation.
    - Changes ShippingPlan status from '지시' to '출하완료'.
    - Updates OrderDetail with shipping quantity and amount.
    - Updates OrderMaster status to '출하완료' if all items are fully shipped.
    """
    for item in received_items:
        plan = item["plan"]
        detail = item["detail"]
        
        # 1. Update the ShippingPlan status
        plan.status = "출하완료"
        
        # 2. Update the corresponding OrderDetail
        detail.shipping_qty = (detail.shipping_qty or 0) + item["received_qty"]
        detail.shipping_amount = Decimal(str(detail.unit_price)) * detail.shipping_qty
        if not detail.actual_shipping_date:
            detail.actual_shipping_date = item["received_date"]

    # 3. Check if the entire order is now complete
    db.flush() # Ensure detail.shipping_qty updates are available for the query
    
    all_details = db.query(OrderDetail).filter_by(order_no=order.order_no).all()
    
    is_order_complete = all(
        (d.shipping_qty or 0) >= d.order_qty for d in all_details
    )
    
    if is_order_complete:
        order.status = "출하완료"
        
    db.commit()

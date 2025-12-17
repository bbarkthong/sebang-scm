
from database.models import OrderMaster, OrderDetail, Warehouse, ShippingPlan

def get_orders_for_shipping_plan(db):
    """Fetches orders that are fully received and ready for shipping plan creation."""
    return db.query(OrderMaster).filter(
        OrderMaster.status == "입고완료"
    ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()

def get_item_inventory_status(db, order_no, order_seq):
    """
    Calculates the detailed inventory status for a single order item.
    """
    # Sum of all received items
    receipts = db.query(Warehouse.received_qty).filter_by(order_no=order_no, order_seq=order_seq).all()
    total_received = sum(r[0] for r in receipts)
    
    # Sum of items already planned or instructed for shipping
    planned_items = db.query(ShippingPlan.planned_qty).filter(
        ShippingPlan.order_no == order_no,
        ShippingPlan.order_seq == order_seq,
        ShippingPlan.status.in_(["계획", "지시"])
    ).all()
    total_planned = sum(p[0] for p in planned_items)

    # Sum of items already shipped
    shipped_items = db.query(ShippingPlan.planned_qty).filter_by(
        order_no=order_no, 
        order_seq=order_seq, 
        status="출하완료"
    ).all()
    total_shipped = sum(s[0] for s in shipped_items)

    available_qty = total_received - total_planned - total_shipped
    
    return {
        "received": total_received,
        "planned": total_planned,
        "shipped": total_shipped,
        "available": available_qty
    }

def create_shipping_plans(db, shipping_items, username):
    """Creates new shipping plan entries in the database."""
    for item in shipping_items:
        db.add(ShippingPlan(
            order_no=item["order_no"],
            order_seq=item["order_seq"],
            planned_shipping_date=item["planned_date"],
            planned_qty=item["planned_qty"],
            status="계획",
            created_by=username
        ))
    db.commit()

def get_shipping_plans_for_order(db, order_no):
    """Fetches all shipping plans associated with a given order."""
    return db.query(ShippingPlan).filter_by(order_no=order_no).order_by(
        ShippingPlan.planned_shipping_date, ShippingPlan.order_seq
    ).all()

def instruct_shipping_plans(db, plans):
    """Updates the status of given shipping plans from 'Plan' to 'Instruct'."""
    for plan in plans:
        if plan.status == "계획":
            plan.status = "지시"
    db.commit()

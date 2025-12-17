
from datetime import datetime
from database.models import OrderMaster, OrderDetail

def get_orders_for_approval(db, filters):
    """
    Fetches orders based on filter criteria for the approval page.
    
    Args:
        db: The database session.
        filters (dict): A dictionary containing filter criteria like 
                        'status', 'order_type', 'search_no'.
    """
    query = db.query(OrderMaster).order_by(OrderMaster.created_at.desc())
    
    if filters.get("status") and filters["status"] != "전체":
        query = query.filter(OrderMaster.status == filters["status"])
    
    if filters.get("order_type") and filters["order_type"] != "전체":
        query = query.filter(OrderMaster.order_type == filters["order_type"])
    
    if filters.get("search_no"):
        query = query.filter(OrderMaster.order_no.contains(filters["search_no"]))
    
    return query.all()

def get_order_details(db, order_no):
    """Fetches the details for a single order."""
    master = db.query(OrderMaster).filter(OrderMaster.order_no == order_no).first()
    details = db.query(OrderDetail).filter(OrderDetail.order_no == order_no).order_by(OrderDetail.order_seq).all()
    
    total_amount = 0
    if details:
        total_amount = sum(d.order_qty * d.unit_price for d in details)
        
    return master, details, total_amount

def approve_order(db, order, priority, username):
    """Sets the order status to 'Approved'."""
    order.status = "승인"
    order.priority = priority
    order.approved_by = username
    order.approved_at = datetime.now()
    db.commit()

def reject_order(db, order):
    """Sets the order status to 'Rejected'."""
    order.status = "거부"
    db.commit()

def set_order_in_production(db, order):
    """Sets the order status to 'In Production'."""
    order.status = "생산중"
    db.commit()

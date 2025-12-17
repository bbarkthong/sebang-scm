
from collections import Counter
from database.models import OrderMaster, Warehouse, ShippingPlan

def get_client_dashboard_data(db, username):
    """Fetches all necessary data for the client ('발주사') dashboard."""
    my_orders = db.query(OrderMaster).filter_by(created_by=username).order_by(OrderMaster.created_at.desc()).all()
    if not my_orders:
        return None

    status_counts = Counter(o.status for o in my_orders)
    
    data = {
        "total_orders": len(my_orders),
        "pending_count": status_counts.get("대기", 0),
        "approved_count": status_counts.get("승인", 0) + status_counts.get("생산중", 0),
        "completed_count": status_counts.get("출하완료", 0),
        "recent_orders": my_orders[:10]
    }
    return data

def get_manager_dashboard_data(db):
    """Fetches all necessary data for the order manager ('주문담당자') dashboard."""
    all_orders = db.query(OrderMaster).all()
    status_counts = Counter(o.status for o in all_orders)
    
    urgent_orders = db.query(OrderMaster).filter(
        OrderMaster.order_type == "긴급",
        OrderMaster.status.in_(['대기', '승인', '생산중'])
    ).limit(10).all()
    
    pending_orders = db.query(OrderMaster).filter(
        OrderMaster.status == '대기'
    ).order_by(OrderMaster.created_at).limit(10).all()

    data = {
        "total_orders": len(all_orders),
        "pending_count": status_counts.get("대기", 0),
        "approved_count": status_counts.get("승인", 0),
        "warehousing_complete_count": status_counts.get("입고완료", 0),
        "shipping_complete_count": status_counts.get("출하완료", 0),
        "urgent_orders": urgent_orders,
        "pending_orders": pending_orders,
    }
    return data

def get_manufacturer_dashboard_data(db, username):
    """Fetches all necessary data for the manufacturer ('제조담당자') dashboard."""
    prod_orders = db.query(OrderMaster).filter(OrderMaster.status.in_(['승인', '생산중'])).all()
    status_counts = Counter(o.status for o in prod_orders)
    
    recent_receipts = db.query(Warehouse).filter_by(received_by=username).order_by(Warehouse.created_at.desc()).limit(10).all()

    data = {
        "production_pending_count": status_counts.get("승인", 0),
        "in_production_count": status_counts.get("생산중", 0),
        "production_orders": prod_orders[:20],
        "recent_receipts": recent_receipts,
    }
    return data

def get_common_activity_data(db):
    """Fetches recent activities for all users."""
    recent_orders = db.query(OrderMaster).order_by(OrderMaster.created_at.desc()).limit(5).all()
    return {"recent_orders": recent_orders}


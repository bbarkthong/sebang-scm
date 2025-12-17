
from database.models import OrderMaster, OrderDetail, Warehouse

def get_orders_for_warehousing(db):
    """Fetches orders that are ready for warehousing ('Approved' or 'In Production')."""
    return db.query(OrderMaster).filter(
        OrderMaster.status.in_(["승인", "생산중"])
    ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()

def get_order_receipt_status(db, order_no):
    """
    Calculates the receipt progress and quantities for a given order.
    Returns a dictionary with total ordered, total received, and progress percentage.
    """
    order_details = db.query(OrderDetail).filter(OrderDetail.order_no == order_no).all()
    if not order_details:
        return {"ordered": 0, "received": 0, "progress": 0}
    
    total_ordered = sum(d.order_qty for d in order_details)
    
    # Sum up all received quantities for the order
    receipts = db.query(Warehouse.received_qty).filter(Warehouse.order_no == order_no).all()
    total_received = sum(r[0] for r in receipts)
    
    progress = (total_received / total_ordered * 100) if total_ordered > 0 else 0
    
    return {"ordered": total_ordered, "received": total_received, "progress": progress}

def get_detailed_receipt_status(db, order_no):
    """
    Gets the receipt status for each line item in an order.
    Returns a list of dictionaries, each containing detail, received_qty, and remaining_qty.
    """
    order_details = db.query(OrderDetail).filter(OrderDetail.order_no == order_no).order_by(OrderDetail.order_seq).all()
    if not order_details:
        return []

    # Get a summary of all receipts for the order to avoid querying in a loop
    receipt_summary = {}
    receipts = db.query(Warehouse.order_seq, Warehouse.received_qty).filter(Warehouse.order_no == order_no).all()
    for seq, qty in receipts:
        receipt_summary[seq] = receipt_summary.get(seq, 0) + qty

    status_list = []
    for detail in order_details:
        received_qty = receipt_summary.get(detail.order_seq, 0)
        status_list.append({
            "detail": detail,
            "received_qty": received_qty,
            "remaining_qty": detail.order_qty - received_qty,
        })
    return status_list

def register_receipts(db, order, receipt_items, username):
    """
    Registers new warehouse receipts and updates the order status.
    """
    # Add new warehouse entries
    for item in receipt_items:
        db.add(Warehouse(
            order_no=item["order_no"],
            order_seq=item["order_seq"],
            item_code=item["item_code"],
            item_name=item["item_name"],
            received_qty=item["received_qty"],
            received_date=item["received_date"],
            received_by=username
        ))
    
    # Update status to 'In Production' if it was 'Approved'
    if order.status == "승인":
        order.status = "생산중"

    # Flush to make the new receipts available for the progress calculation
    db.flush()
    
    # Check if the order is now fully received
    status = get_order_receipt_status(db, order.order_no)
    if status["progress"] >= 100:
        order.status = "입고완료"
    
    db.commit()

def get_receipt_history(db, order_no):
    """Fetches the history of warehouse receipts for a given order."""
    return db.query(Warehouse).filter(
        Warehouse.order_no == order_no
    ).order_by(Warehouse.received_date.desc(), Warehouse.order_seq).all()

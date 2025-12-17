
from decimal import Decimal
from database.models import OrderMaster, OrderDetail, ItemMaster
from utils.order_utils import generate_order_no
from utils.excel_handler import parse_excel_file

def get_active_items(db):
    """Fetches all active items from the ItemMaster."""
    return db.query(ItemMaster).filter(ItemMaster.is_active == "Y").order_by(ItemMaster.item_name).all()

def create_order(db, user, order_data, details):
    """
    Creates a new order in the database with its details.

    Args:
        db: The database session.
        user (dict): The current user information.
        order_data (dict): Contains master info like 'order_date', 'order_type', 'customer_company'.
        details (list): A list of dictionaries for each order detail.
    """
    # Generate a fresh order number upon final submission
    order_no = generate_order_no(order_data['order_date'])
    
    # Create OrderMaster
    order_master = OrderMaster(
        order_no=order_no,
        order_date=order_data['order_date'],
        order_type=order_data['order_type'],
        customer_company=order_data['customer_company'],
        status="대기",
        created_by=user["username"]
    )
    db.add(order_master)
    
    # Create OrderDetail entries
    for idx, detail in enumerate(details):
        order_detail = OrderDetail(
            order_no=order_no,
            order_seq=idx + 1,
            item_code=detail["item_code"],
            item_name=detail["item_name"],
            order_qty=detail["order_qty"],
            unit_price=Decimal(str(detail["unit_price"])),
            planned_shipping_date=detail["planned_shipping_date"]
        )
        db.add(order_detail)
        
    db.commit()
    return order_no

def process_excel_file(uploaded_file):
    """
    Parses an uploaded Excel file and returns the structured order details.
    This is a wrapper around the existing excel_handler functionality.
    """
    return parse_excel_file(uploaded_file)

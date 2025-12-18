import streamlit as st
import pandas as pd
from auth.auth import get_current_user
from database.connection import get_db, close_db
from utils.validators import validate_priority
from utils.order_dialog import show_order_detail_modal
from config import PRIORITY_MIN, PRIORITY_MAX, PRIORITY_DEFAULT, ORDER_STATUS
from services.approval_service import (
    get_orders_for_approval,
    get_order_details,
    approve_order,
    reject_order,
    set_order_in_production
)

def show_page():
    """
    Renders the Order Approval page with an improved UX.
    """
    st.title("주문 승인")
    st.markdown("---")

    user = get_current_user()
    db = get_db()
    try:
        render_page_content(db, user)
    finally:
        close_db(db)

def render_page_content(db, user):
    """
    Renders the main content of the page with a card-based layout.
    """
    # --- Filter Options ---
    col1, col2, col3 = st.columns(3)
    filters = {
        "status": col1.selectbox("상태 필터", ["전체"] + list(ORDER_STATUS.keys())),
        "order_type": col2.selectbox("주문구분 필터", ["전체", "긴급", "일반"]),
        "search_no": col3.text_input("주문번호 검색"),
    }

    orders = get_orders_for_approval(db, filters)

    if not orders:
        st.info("조회된 주문이 없습니다.")
        return

    st.markdown(f"### 주문 목록 (총 {len(orders)}건)")
    
    # 헤더
    header_cols = st.columns([2, 2, 2, 2, 1])
    header_cols[0].write("**주문번호**")
    header_cols[1].write("**고객사**")
    header_cols[2].write("**주문일자**")
    header_cols[3].write("**상태**")
    header_cols[4].write("**상세보기**")
    st.markdown("---")
    
    # --- Interactive Order List ---
    for order in orders:
        # Fetch details for each order
        _ , details, total_amount = get_order_details(db, order.order_no)
        
        # 주문 행
        row_cols = st.columns([2, 2, 2, 2, 1])
        row_cols[0].write(order.order_no)
        row_cols[1].write(order.customer_company)
        row_cols[2].write(order.order_date.strftime('%Y-%m-%d'))
        row_cols[3].write(order.status)
        with row_cols[4]:
            if st.button("📋", key=f"detail_{order.order_no}", help=f"{order.order_no} 상세보기"):
                show_order_detail_modal(order.order_no)
        
        # 주문 상세 및 승인 폼 (expander로 표시)
        with st.expander(f"주문 상세 및 처리: {order.order_no}", expanded=False):
            render_order_details(order, details, total_amount)
            render_approval_form(db, user, order)

def render_order_details(order, details, total_amount):
    """Displays the master and detail information for a selected order."""
    col1, col2 = st.columns(2)
    col1.metric("총 주문금액", f"{total_amount:,.0f}원")
    col2.metric("우선순위", order.priority or "N/A")

    st.markdown("#### 주문 상세")
    if details:
        detail_df = pd.DataFrame([{
            "순번": d.order_seq, "품목명": d.item_name, "주문수량": f"{d.order_qty:,}",
        } for d in details])
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

def render_approval_form(db, user, order):
    """Renders the form for approving, rejecting, or changing status, with unique keys."""
    if order.status == "대기":
        st.markdown("##### 주문 승인/거부")
        # Use order.id or order_no in the key to ensure form uniqueness
        with st.form(key=f"approval_form_{order.order_no}"):
            priority = st.number_input(
                "우선순위", min_value=PRIORITY_MIN, max_value=PRIORITY_MAX, 
                value=order.priority or PRIORITY_DEFAULT, key=f"priority_{order.order_no}"
            )
            action = st.radio("처리", ["승인", "거부"], horizontal=True, key=f"action_{order.order_no}")

            if st.form_submit_button("처리", use_container_width=True, type="primary"):
                is_valid, msg = validate_priority(priority)
                if not is_valid:
                    st.error(msg)
                else:
                    if action == "승인":
                        approve_order(db, order, priority, user["username"])
                        st.success(f"주문 {order.order_no}이(가) 승인되었습니다.")
                    else:
                        reject_order(db, order)
                        st.success(f"주문 {order.order_no}이(가) 거부되었습니다.")
                    st.rerun()

    elif order.status == "승인":
        if st.button("생산중으로 상태 변경", key=f"in_prod_{order.order_no}", type="primary"):
            set_order_in_production(db, order)
            st.success(f"주문 {order.order_no}의 상태가 변경되었습니다.")
            st.rerun()
    else:
        st.info(f"이 주문은 현재 작업을 수행할 수 없는 '{order.status}' 상태입니다.")
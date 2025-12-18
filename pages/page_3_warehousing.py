import streamlit as st
import pandas as pd
from datetime import date
from auth.auth import get_current_user
from database.connection import get_db, close_db
from utils.order_dialog import show_order_detail_modal
from services.warehousing_service import (
    get_orders_for_warehousing,
    get_order_receipt_status,
    get_detailed_receipt_status,
    register_receipts,
    get_receipt_history,
)

def show_page():
    """
    Renders the Warehousing (Goods Receipt) page with an improved UX.
    """
    st.title("입고 등록")
    st.markdown("---")

    user = get_current_user()
    db = get_db()
    try:
        render_page_content(db, user)
    finally:
        close_db(db)

def render_page_content(db, user):
    """
    Renders the main content with an expander-based layout.
    """
    orders_to_process = get_orders_for_warehousing(db)

    if not orders_to_process:
        st.info("입고 등록 가능한 주문이 없습니다.")
        return

    st.markdown(f"### 입고 등록 가능 주문 (총 {len(orders_to_process)}건)")
    
    for order in orders_to_process:
        status = get_order_receipt_status(db, order.order_no)
        
        # 주문 카드 레이아웃
        col1, col2 = st.columns([5, 1])
        with col1:
            expander_title = (
                f"**{order.order_no}** | {order.customer_company} | "
                f"**상태: {order.status}** | "
                f"**진행률: {status['progress']:.1f}%**"
            )
            
            with st.expander(expander_title):
                render_receipt_form(db, user, order)
                render_receipt_history(db, order.order_no)
        with col2:
            if st.button("📋", key=f"detail_{order.order_no}", help=f"{order.order_no} 상세보기"):
                show_order_detail_modal(order.order_no)

def render_receipt_form(db, user, order):
    """Renders the form for registering incoming goods for a specific order."""
    detailed_status = get_detailed_receipt_status(db, order.order_no)
    if not detailed_status:
        st.warning("주문 상세 정보가 없습니다.")
        return

    with st.form(key=f"warehouse_form_{order.order_no}"):
        st.markdown("#### 입고 항목 입력")
        
        receipt_items = []
        items_with_remaining_qty = [s for s in detailed_status if s["remaining_qty"] > 0]

        for item_status in items_with_remaining_qty:
            detail = item_status["detail"]
            cols = st.columns([2, 1, 1])
            cols[0].markdown(f"**{detail.item_name}** <br> <small>잔량: {item_status['remaining_qty']:,}</small>", unsafe_allow_html=True)
            
            qty_in = cols[1].number_input("입고수량", 0, item_status["remaining_qty"], item_status["remaining_qty"], key=f"qty_{detail.order_no}_{detail.order_seq}")
            date_in = cols[2].date_input("입고일자", date.today(), key=f"date_{detail.order_no}_{detail.order_seq}")
            
            if qty_in > 0:
                receipt_items.append({
                    "order_no": detail.order_no, "order_seq": detail.order_seq,
                    "item_code": detail.item_code, "item_name": detail.item_name,
                    "received_qty": qty_in, "received_date": date_in
                })
        
        if not items_with_remaining_qty:
            st.info("모든 항목이 이미 입고 완료되었습니다.")
        
        if st.form_submit_button("입고 등록", use_container_width=True, type="primary"):
            if not receipt_items:
                st.warning("입고할 수량을 1 이상 입력해주세요.")
            else:
                try:
                    register_receipts(db, order, receipt_items, user["username"])
                    st.success(f"✅ 주문 {order.order_no}에 대한 입고 등록이 완료되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 입고 등록 중 오류 발생: {e}")

def render_receipt_history(db, order_no):
    """Displays the history of receipts for the given order."""
    st.markdown("##### 입고 내역")
    history = get_receipt_history(db, order_no)
    if history:
        history_df = pd.DataFrame([{
            "입고일자": r.received_date.strftime("%Y-%m-%d"), "품목명": r.item_name,
            "입고수량": f"{r.received_qty:,}", "입고자": r.received_by
        } for r in history])
        st.dataframe(history_df, use_container_width=True, hide_index=True, height=150)
    else:
        st.info("입고 내역이 없습니다.")
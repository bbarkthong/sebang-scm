import streamlit as st
import pandas as pd
from datetime import date
from auth.auth import get_current_user
from database.connection import get_db, close_db
from database.models import OrderDetail
from services.shipping_registration_service import (
    get_orders_for_registration,
    get_plans_for_registration,
    confirm_shipment_received,
)

def show_page():
    """
    Renders the Shipping Registration page for clients with an improved UX.
    """
    st.title("출하 등록 (수신 확인)")
    st.markdown("---")

    user = get_current_user()
    db = get_db()
    try:
        render_page_content(db, user)
    finally:
        close_db(db)

def render_page_content(db, user):
    """
    Renders the main content of the page with an expander-based layout.
    """
    st.subheader("출하 완료 등록")

    orders_to_register = get_orders_for_registration(db, user.get("company_name", ""))

    if not orders_to_register:
        st.info("출하 완료 등록할 주문이 없습니다.")
        return

    for order in orders_to_register:
        expander_title = f"**{order.order_no}** | {order.order_date.strftime('%Y-%m-%d')}"
        with st.expander(expander_title):
            render_confirmation_form(db, user, order)

def render_confirmation_form(db, user, order):
    """
    Renders the form for a client to confirm receipt of goods for a specific order.
    """
    with st.form(key=f"receipt_form_{order.order_no}"):
        st.markdown("#### 수신 항목 확인")
        
        received_items = []
        plans_to_update = get_plans_for_registration(db, order.order_no)

        for plan in plans_to_update:
            detail = db.query(OrderDetail).filter_by(order_no=plan.order_no, order_seq=plan.order_seq).first()
            if not detail: continue

            cols = st.columns([2, 1, 1])
            cols[0].markdown(f"**{detail.item_name}** <br> <small>출하예정일: {plan.planned_shipping_date.strftime('%Y-%m-%d')}</small>", unsafe_allow_html=True)
            cols[1].write(f"계획수량: {plan.planned_qty:,}")
            
            received_qty = cols[2].number_input("수신수량", 0, plan.planned_qty, plan.planned_qty, key=f"qty_{plan.plan_id}")
            
            if received_qty > 0:
                received_items.append({
                    "plan": plan, "detail": detail,
                    "received_qty": received_qty, "received_date": date.today()
                })
        
        if not received_items:
            st.warning("등록할 항목이 없습니다.")

        if st.form_submit_button("출하 완료 등록", use_container_width=True, type="primary"):
            if received_items:
                try:
                    confirm_shipment_received(db, order, received_items)
                    st.success("출하 완료가 성공적으로 등록되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"출하 등록 중 오류 발생: {e}")
            else:
                st.warning("수신수량을 1 이상 입력해야 합니다.")
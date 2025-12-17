import streamlit as st
import pandas as pd
from datetime import date
from auth.auth import get_current_user
from database.connection import get_db, close_db
from database.models import OrderDetail
from services.shipping_service import (
    get_orders_for_shipping_plan,
    get_item_inventory_status,
    create_shipping_plans,
    get_shipping_plans_for_order,
    instruct_shipping_plans,
)

def show_page():
    """
    Renders the Shipping Plan page with an improved UX.
    """
    st.title("출하 계획")
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
    st.subheader("출하 계획 수립")
    
    orders_for_planning = get_orders_for_shipping_plan(db)
    
    if not orders_for_planning:
        st.warning("⚠️ 출하 계획을 수립할 주문이 없습니다.")
        return

    for order in orders_for_planning:
        expander_title = f"**{order.order_no}** | {order.customer_company} | {order.order_date.strftime('%Y-%m-%d')}"
        with st.expander(expander_title):
            render_shipping_item_form(db, user, order)
            render_shipping_plan_history(db, order)

def render_shipping_item_form(db, user, order):
    """Renders the form to input shipping quantities and dates for a specific order."""
    with st.form(key=f"shipping_plan_form_{order.order_no}"):
        st.markdown("#### 출하 계획 입력")
        
        shipping_items = []
        details = db.query(OrderDetail).filter_by(order_no=order.order_no).all()

        for detail in details:
            inventory = get_item_inventory_status(db, detail.order_no, detail.order_seq)
            available_qty = inventory["available"]

            if available_qty > 0:
                cols = st.columns([2, 1, 1])
                cols[0].markdown(f"**{detail.item_name}**")
                cols[1].markdown(f"가용재고: {available_qty:,}")
                
                planned_qty = cols[2].number_input("출하수량", 0, available_qty, available_qty, key=f"qty_{detail.order_no}_{detail.order_seq}")
                
                if planned_qty > 0:
                    shipping_items.append({
                        "order_no": detail.order_no, "order_seq": detail.order_seq,
                        "planned_qty": planned_qty, "planned_date": date.today() # Simplified for this UX pass
                    })
        
        if not shipping_items:
            st.info("출하 계획을 수립할 가용 재고가 없습니다.")

        if st.form_submit_button("📄 출하 계획 등록", use_container_width=True, type="primary"):
            if shipping_items:
                try:
                    create_shipping_plans(db, shipping_items, user["username"])
                    st.success(f"✅ {len(shipping_items)}개 항목의 출하 계획이 등록되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 출하 계획 등록 중 오류: {e}")
            else:
                st.warning("출하할 항목이 없습니다.")

def render_shipping_plan_history(db, order):
    """Displays the history of shipping plans and allows for actions."""
    st.markdown("##### 출하 계획 내역")
    
    plans = get_shipping_plans_for_order(db, order.order_no)
    if not plans:
        st.info("출하 계획 내역이 없습니다.")
        return

    plan_df = pd.DataFrame([{
        "품목명": db.query(OrderDetail.item_name).filter_by(order_no=p.order_no, order_seq=p.order_seq).scalar(),
        "출하수량": p.planned_qty, "출하예정일": p.planned_shipping_date.strftime('%Y-%m-%d'), "상태": p.status
    } for p in plans])
    st.dataframe(plan_df, use_container_width=True, hide_index=True)

    pending_plans = [p for p in plans if p.status == "계획"]
    if pending_plans:
        if st.button("📤 출하 지시", key=f"instruct_{order.order_no}", type="primary"):
            try:
                instruct_shipping_plans(db, pending_plans)
                st.success(f"✅ {len(pending_plans)}개 항목에 대한 출하 지시가 완료되었습니다.")
                st.rerun()
            except Exception as e:
                db.rollback()
                st.error(f"❌ 출하 지시 중 오류: {e}")
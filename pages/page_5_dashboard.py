
import streamlit as st
import pandas as pd
from auth.auth import get_current_user
from database.connection import get_db, close_db
from utils.order_dialog import show_order_detail_modal
from services.dashboard_service import (
    get_client_dashboard_data,
    get_manager_dashboard_data,
    get_manufacturer_dashboard_data,
    get_common_activity_data,
)

def show_page():
    """
    Renders the main Dashboard page, routing to the correct view based on user role.
    """
    st.title("대시보드")

    user = get_current_user()
    role = user.get("role", "")

    db = get_db()
    try:
        if role == "발주사":
            data = get_client_dashboard_data(db, user["username"])
            render_client_dashboard(data)
        elif role == "주문담당자":
            data = get_manager_dashboard_data(db)
            render_manager_dashboard(data)
            common_data = get_common_activity_data(db)
            
            common_data = get_common_activity_data(db)
            render_common_activity(common_data)
        elif role == "제조담당자":
            data = get_manufacturer_dashboard_data(db, user["username"])
            render_manufacturer_dashboard(data)
            
            common_data = get_common_activity_data(db)
            render_common_activity(common_data)
        else:
            st.warning("알 수 없는 역할입니다. 대시보드를 표시할 수 없습니다.")
        
    finally:
        close_db(db)

def render_client_dashboard(data):
    """Dashboard for '발주사' (Client)."""
    st.subheader("발주사 대시보드")
    
    if not data:
        st.info("등록된 주문이 없습니다.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 주문", data["total_orders"])
    col2.metric("대기 중", data["pending_count"])
    col3.metric("승인됨", data["approved_count"])
    col4.metric("완료", data["completed_count"])

    st.markdown("### 최근 주문")
    if len(data["recent_orders"]) > 0:
        # 헤더
        header_cols = st.columns([2, 2, 2, 2, 1])
        header_cols[0].write("**주문번호**")
        header_cols[1].write("**주문일자**")
        header_cols[2].write("**주문구분**")
        header_cols[3].write("**상태**")
        header_cols[4].write("**상세보기**")
        st.markdown("---")
        
        # 각 주문 행
        for order in data["recent_orders"]:
            row_cols = st.columns([2, 2, 2, 2, 1])
            row_cols[0].write(order.order_no)
            row_cols[1].write(order.order_date.strftime("%Y-%m-%d"))
            row_cols[2].write(order.order_type)
            row_cols[3].write(order.status)
            with row_cols[4]:
                if st.button("📋", key=f"detail_recent_{order.order_no}", help=f"{order.order_no} 상세보기"):
                    show_order_detail_modal(order.order_no)
    else:
        st.info("등록된 주문이 없습니다.")

def render_manager_dashboard(data):
    """Dashboard for '주문담당자' (Order Manager)."""
    st.subheader("주문담당자 대시보드")

    cols = st.columns(5)
    cols[0].metric("전체 주문", data["total_orders"])
    cols[1].metric("대기", data["pending_count"])
    cols[2].metric("승인", data["approved_count"])
    cols[3].metric("입고완료", data["warehousing_complete_count"])
    cols[4].metric("출하완료", data["shipping_complete_count"])

    if data["urgent_orders"]:
        st.markdown("### 긴급 주문")
        # 헤더
        header_cols = st.columns([2, 2, 2, 1])
        header_cols[0].write("**주문번호**")
        header_cols[1].write("**고객사**")
        header_cols[2].write("**상태**")
        header_cols[3].write("**상세보기**")
        st.markdown("---")
        
        # 각 주문 행
        for order in data["urgent_orders"]:
            row_cols = st.columns([2, 2, 2, 1])
            row_cols[0].write(order.order_no)
            row_cols[1].write(order.customer_company)
            row_cols[2].write(order.status)
            with row_cols[3]:
                if st.button("📋", key=f"detail_urgent_{order.order_no}", help=f"{order.order_no} 상세보기"):
                    show_order_detail_modal(order.order_no)
    
    if data["pending_orders"]:
        st.markdown("### 승인 대기 주문")
        # 헤더
        header_cols = st.columns([2, 2, 2, 1])
        header_cols[0].write("**주문번호**")
        header_cols[1].write("**고객사**")
        header_cols[2].write("**주문일자**")
        header_cols[3].write("**상세보기**")
        st.markdown("---")
        
        # 각 주문 행
        for order in data["pending_orders"]:
            row_cols = st.columns([2, 2, 2, 1])
            row_cols[0].write(order.order_no)
            row_cols[1].write(order.customer_company)
            row_cols[2].write(order.order_date.strftime('%Y-%m-%d'))
            with row_cols[3]:
                if st.button("📋", key=f"detail_pending_{order.order_no}", help=f"{order.order_no} 상세보기"):
                    show_order_detail_modal(order.order_no)

def render_manufacturer_dashboard(data):
    """Dashboard for '제조담당자' (Manufacturer)."""
    st.subheader("제조담당자 대시보드")
    
    col1, col2 = st.columns(2)
    col1.metric("생산 대기", data["production_pending_count"])
    col2.metric("생산 중", data["in_production_count"])

    if data["production_orders"]:
        st.markdown("### 생산 주문 목록")
        # 헤더
        header_cols = st.columns([2, 2, 2, 1, 1])
        header_cols[0].write("**주문번호**")
        header_cols[1].write("**고객사**")
        header_cols[2].write("**상태**")
        header_cols[3].write("**우선순위**")
        header_cols[4].write("**상세보기**")
        st.markdown("---")
        
        # 각 주문 행
        for order in data["production_orders"]:
            row_cols = st.columns([2, 2, 2, 1, 1])
            row_cols[0].write(order.order_no)
            row_cols[1].write(order.customer_company)
            row_cols[2].write(order.status)
            row_cols[3].write(order.priority or "N/A")
            with row_cols[4]:
                if st.button("📋", key=f"detail_prod_{order.order_no}", help=f"{order.order_no} 상세보기"):
                    show_order_detail_modal(order.order_no)

    if data["recent_receipts"]:
        st.markdown("### 최근 입고 내역")
        df = pd.DataFrame([{"입고일자": r.received_date.strftime('%Y-%m-%d'), "주문번호": r.order_no, "품목명": r.item_name} for r in data["recent_receipts"]])
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_common_activity(data):
    """Renders the common recent activity log for all users."""
    st.markdown("---")
    st.markdown("### 최근 활동")
    if data["recent_orders"]:
        df = pd.DataFrame([{
            "일시": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
            "활동": f"주문 등록: {o.order_no}",
            "담당자": o.created_by, "상태": o.status
        } for o in data["recent_orders"]])
        st.dataframe(df, use_container_width=True, hide_index=True)

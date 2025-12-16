"""
대시보드 페이지
"""
import streamlit as st
from datetime import datetime, timedelta
from auth.auth import require_auth, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail, Warehouse, ShippingPlan
import pandas as pd

# 인증 확인
require_auth()

st.title("대시보드")
st.markdown("---")

user = get_current_user()
user_role = user.get("role", "")

db = get_db()
try:
    # 역할별 대시보드
    if user_role == "발주사":
        st.subheader("발주사 대시보드")
        
        # 내 주문 현황
        my_orders = db.query(OrderMaster).filter(
            OrderMaster.created_by == user["username"]
        ).order_by(OrderMaster.created_at.desc()).all()
        
        if my_orders:
            # 통계
            col1, col2, col3, col4 = st.columns(4)
            
            status_counts = {}
            for order in my_orders:
                status_counts[order.status] = status_counts.get(order.status, 0) + 1
            
            with col1:
                st.metric("전체 주문", len(my_orders))
            with col2:
                st.metric("대기 중", status_counts.get("대기", 0))
            with col3:
                st.metric("승인됨", status_counts.get("승인", 0) + status_counts.get("생산중", 0))
            with col4:
                st.metric("완료", status_counts.get("출하완료", 0))
            
            # 최근 주문 목록
            st.markdown("### 최근 주문")
            recent_orders = my_orders[:10]
            order_data = []
            for order in recent_orders:
                order_data.append({
                    "주문번호": order.order_no,
                    "주문일자": order.order_date.strftime("%Y-%m-%d"),
                    "주문구분": order.order_type,
                    "상태": order.status,
                    "우선순위": order.priority,
                    "등록일시": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else ""
                })
            
            df = pd.DataFrame(order_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("등록된 주문이 없습니다.")
    
    elif user_role == "주문담당자":
        st.subheader("주문담당자 대시보드")
        
        # 전체 주문 통계
        all_orders = db.query(OrderMaster).all()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        status_counts = {}
        for order in all_orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
        
        with col1:
            st.metric("전체 주문", len(all_orders))
        with col2:
            st.metric("대기", status_counts.get("대기", 0))
        with col3:
            st.metric("승인", status_counts.get("승인", 0))
        with col4:
            st.metric("입고완료", status_counts.get("입고완료", 0))
        with col5:
            st.metric("출하완료", status_counts.get("출하완료", 0))
        
        # 긴급 주문
        urgent_orders = db.query(OrderMaster).filter(
            OrderMaster.order_type == "긴급",
            OrderMaster.status.in_(["대기", "승인", "생산중"])
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).limit(10).all()
        
        if urgent_orders:
            st.markdown("### 긴급 주문")
            urgent_data = []
            for order in urgent_orders:
                urgent_data.append({
                    "주문번호": order.order_no,
                    "고객사": order.customer_company,
                    "주문일자": order.order_date.strftime("%Y-%m-%d"),
                    "상태": order.status,
                    "우선순위": order.priority
                })
            
            urgent_df = pd.DataFrame(urgent_data)
            st.dataframe(urgent_df, use_container_width=True, hide_index=True)
        
        # 승인 대기 주문
        pending_orders = db.query(OrderMaster).filter(
            OrderMaster.status == "대기"
        ).order_by(OrderMaster.created_at).limit(10).all()
        
        if pending_orders:
            st.markdown("### 승인 대기 주문")
            pending_data = []
            for order in pending_orders:
                pending_data.append({
                    "주문번호": order.order_no,
                    "고객사": order.customer_company,
                    "주문일자": order.order_date.strftime("%Y-%m-%d"),
                    "주문구분": order.order_type,
                    "등록일시": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else ""
                })
            
            pending_df = pd.DataFrame(pending_data)
            st.dataframe(pending_df, use_container_width=True, hide_index=True)
        
        # 출하 계획 현황
        shipping_plans = db.query(ShippingPlan).filter(
            ShippingPlan.status == "계획"
        ).order_by(ShippingPlan.planned_shipping_date).limit(10).all()
        
        if shipping_plans:
            st.markdown("### 출하 예정 계획")
            plan_data = []
            for plan in shipping_plans:
                order = db.query(OrderMaster).filter(
                    OrderMaster.order_no == plan.order_no
                ).first()
                detail = db.query(OrderDetail).filter(
                    OrderDetail.order_no == plan.order_no,
                    OrderDetail.order_seq == plan.order_seq
                ).first()
                
                plan_data.append({
                    "주문번호": plan.order_no,
                    "고객사": order.customer_company if order else "",
                    "품목명": detail.item_name if detail else "",
                    "출하수량": f"{plan.planned_qty:,}",
                    "출하예정일": plan.planned_shipping_date.strftime("%Y-%m-%d")
                })
            
            plan_df = pd.DataFrame(plan_data)
            st.dataframe(plan_df, use_container_width=True, hide_index=True)
    
    elif user_role == "제조담당자":
        st.subheader("제조담당자 대시보드")
        
        # 생산 대기 주문
        production_orders = db.query(OrderMaster).filter(
            OrderMaster.status.in_(["승인", "생산중"])
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("생산 대기", len([o for o in production_orders if o.status == "승인"]))
        with col2:
            st.metric("생산 중", len([o for o in production_orders if o.status == "생산중"]))
        
        if production_orders:
            st.markdown("### 생산 주문 목록")
            prod_data = []
            for order in production_orders[:20]:
                prod_data.append({
                    "주문번호": order.order_no,
                    "고객사": order.customer_company,
                    "주문일자": order.order_date.strftime("%Y-%m-%d"),
                    "주문구분": order.order_type,
                    "상태": order.status,
                    "우선순위": order.priority
                })
            
            prod_df = pd.DataFrame(prod_data)
            st.dataframe(prod_df, use_container_width=True, hide_index=True)
        
        # 최근 입고 내역
        recent_receipts = db.query(Warehouse).filter(
            Warehouse.received_by == user["username"]
        ).order_by(Warehouse.created_at.desc()).limit(10).all()
        
        if recent_receipts:
            st.markdown("### 최근 입고 내역")
            receipt_data = []
            for receipt in recent_receipts:
                receipt_data.append({
                    "입고일자": receipt.received_date.strftime("%Y-%m-%d"),
                    "주문번호": receipt.order_no,
                    "품목명": receipt.item_name,
                    "입고수량": f"{receipt.received_qty:,}"
                })
            
            receipt_df = pd.DataFrame(receipt_data)
            st.dataframe(receipt_df, use_container_width=True, hide_index=True)
    
    # 공통: 최근 활동
    st.markdown("---")
    st.markdown("### 최근 활동")
    
    # 최근 주문 (전체)
    recent_orders_all = db.query(OrderMaster).order_by(
        OrderMaster.created_at.desc()
    ).limit(5).all()
    
    if recent_orders_all:
        recent_data = []
        for order in recent_orders_all:
            recent_data.append({
                "일시": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
                "활동": f"주문 등록: {order.order_no}",
                "담당자": order.created_by,
                "상태": order.status
            })
        
        recent_df = pd.DataFrame(recent_data)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"오류 발생: {str(e)}")
finally:
    close_db(db)


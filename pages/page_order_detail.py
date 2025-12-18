"""
주문 상세보기 페이지
"""
import streamlit as st
import pandas as pd
from database.connection import get_db, close_db
from services.approval_service import get_order_details
from services.warehousing_service import get_detailed_receipt_status, get_receipt_history
from services.shipping_service import get_item_inventory_status, get_shipping_plans_for_order
from database.models import OrderDetail


def show_page():
    """주문 상세보기 페이지를 렌더링합니다."""
    # 페이지가 호출되는지 확인하기 위한 기본 표시
    st.title("📋 주문 상세보기")
    st.markdown("---")
    
    # session_state에서 주문번호 가져오기
    order_no = st.session_state.get("order_detail_no", None)
    
    if not order_no:
        st.warning("⚠️ 주문번호가 지정되지 않았습니다.")
        st.info("주문 목록에서 상세보기 버튼(📋)을 클릭해주세요.")
        
        # 뒤로가기 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← 뒤로가기", type="secondary", use_container_width=True):
                # 이전 페이지로 이동
                if "order_detail_no" in st.session_state:
                    del st.session_state.order_detail_no
                st.session_state.current_page = "대시보드"
                st.rerun()
        return
    
    # 주문 상세 정보 조회 및 표시
    db = get_db()
    try:
        # 주문 정보 조회
        master, details, total_amount = get_order_details(db, order_no)
    
        if not master:
            st.error(f"주문 정보를 찾을 수 없습니다. (주문번호: {order_no})")
            # 뒤로가기 버튼
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("← 뒤로가기", type="secondary", use_container_width=True):
                    if "order_detail_no" in st.session_state:
                        del st.session_state.order_detail_no
                    st.session_state.current_page = "주문승인"
                    st.rerun()
            return
        
        # 주문 마스터 정보 표시
        st.markdown("### 주문 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**주문번호:** {master.order_no}")
            st.markdown(f"**주문일자:** {master.order_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**고객사:** {master.customer_company}")
            st.markdown(f"**주문구분:** {master.order_type}")
        
        with col2:
            st.markdown(f"**상태:** {master.status}")
            st.markdown(f"**우선순위:** {master.priority or 'N/A'}")
            if master.approved_by:
                st.markdown(f"**승인자:** {master.approved_by}")
                if master.approved_at:
                    st.markdown(f"**승인일시:** {master.approved_at.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**등록자:** {master.created_by}")
            st.markdown(f"**등록일시:** {master.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("---")
        
        # 총 주문금액
        st.metric("총 주문금액", f"{total_amount:,.0f}원")
        
        st.markdown("---")
        
        # 주문 상세 정보
        st.markdown("#### 주문 상세")
        if details:
            detail_data = []
            for detail in details:
                detail_data.append({
                    "순번": detail.order_seq,
                    "품목명": detail.item_name,
                    "주문수량": f"{detail.order_qty:,}",
                    "단가": f"{detail.unit_price:,.0f}원",
                    "금액": f"{detail.order_qty * detail.unit_price:,.0f}원",
                    "출하수량": f"{detail.shipping_qty:,}" if detail.shipping_qty else "0",
                    "출하금액": f"{detail.shipping_amount:,.0f}원" if detail.shipping_amount else "0원",
                })
            
            detail_df = pd.DataFrame(detail_data)
            st.dataframe(detail_df, use_container_width=True, hide_index=True)
        else:
            st.info("주문 상세 정보가 없습니다.")
        
        # 입고 상태 정보
        receipt_status = get_detailed_receipt_status(db, order_no)
        if receipt_status:
            st.markdown("---")
            st.markdown("#### 입고 상태")
            receipt_data = []
            for status in receipt_status:
                detail = status["detail"]
                receipt_data.append({
                    "품목명": detail.item_name,
                    "주문수량": f"{detail.order_qty:,}",
                    "입고수량": f"{status['received_qty']:,}",
                    "잔량": f"{status['remaining_qty']:,}",
                    "진행률": f"{(status['received_qty'] / detail.order_qty * 100):.1f}%" if detail.order_qty > 0 else "0%"
                })
            
            receipt_df = pd.DataFrame(receipt_data)
            st.dataframe(receipt_df, use_container_width=True, hide_index=True)
            
            # 입고 내역
            receipt_history = get_receipt_history(db, order_no)
            if receipt_history:
                with st.expander("입고 내역"):
                    history_data = []
                    for receipt in receipt_history:
                        history_data.append({
                            "입고일자": receipt.received_date.strftime("%Y-%m-%d"),
                            "품목명": receipt.item_name,
                            "입고수량": f"{receipt.received_qty:,}",
                            "입고자": receipt.received_by
                        })
                    history_df = pd.DataFrame(history_data)
                    st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # 출하 계획/상태 정보
        shipping_plans = get_shipping_plans_for_order(db, order_no)
        if shipping_plans:
            st.markdown("---")
            st.markdown("#### 출하 계획/상태")
            plan_data = []
            for plan in shipping_plans:
                detail = db.query(OrderDetail).filter_by(order_no=plan.order_no, order_seq=plan.order_seq).first()
                item_name = detail.item_name if detail else "N/A"
                plan_data.append({
                    "품목명": item_name,
                    "출하수량": f"{plan.planned_qty:,}",
                    "출하예정일": plan.planned_shipping_date.strftime('%Y-%m-%d') if plan.planned_shipping_date else "N/A",
                    "상태": plan.status,
                    "등록일시": plan.created_at.strftime('%Y-%m-%d %H:%M') if plan.created_at else "N/A"
                })
            
            plan_df = pd.DataFrame(plan_data)
            st.dataframe(plan_df, use_container_width=True, hide_index=True)
        
        # 재고 상태 정보 (입고가 있는 경우)
        if receipt_status:
            st.markdown("---")
            st.markdown("#### 재고 상태")
            inventory_data = []
            for status in receipt_status:
                detail = status["detail"]
                inventory = get_item_inventory_status(db, detail.order_no, detail.order_seq)
                inventory_data.append({
                    "품목명": detail.item_name,
                    "입고수량": f"{inventory['received']:,}",
                    "계획수량": f"{inventory['planned']:,}",
                    "출하수량": f"{inventory['shipped']:,}",
                    "가용재고": f"{inventory['available']:,}"
                })
            
            inventory_df = pd.DataFrame(inventory_data)
            st.dataframe(inventory_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        close_db(db)
    
    # 뒤로가기 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← 뒤로가기", type="secondary", use_container_width=True):
            # 이전 페이지로 이동 (주문번호 제거)
            if "order_detail_no" in st.session_state:
                del st.session_state.order_detail_no
            st.session_state.current_page = "주문승인"
            st.rerun()


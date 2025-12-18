"""
주문 상세보기 다이얼로그 컴포넌트
"""
import streamlit as st
import pandas as pd
from database.connection import get_db, close_db
from services.approval_service import get_order_details
from services.warehousing_service import get_detailed_receipt_status, get_receipt_history
from services.shipping_service import get_item_inventory_status, get_shipping_plans_for_order
from database.models import OrderDetail


def show_order_detail_modal(order_no):
    """
    주문 상세보기 페이지로 이동합니다.
    
    Args:
        order_no: 주문번호
    """
    # session_state에 주문번호 저장하고 페이지 전환
    st.session_state.order_detail_no = order_no
    st.session_state.current_page = "주문상세"
    st.rerun()


def check_and_render_dialog():
    """session_state를 확인하여 다이얼로그를 렌더링합니다."""
    if "open_order_dialog" not in st.session_state or st.session_state.open_order_dialog is None:
        return
    
    order_no = st.session_state.open_order_dialog
    
    # 다이얼로그를 열기 전에 필요한 모든 데이터를 미리 조회하고 딕셔너리로 변환
    db = get_db()
    try:
        # 주문 정보 조회
        master, details, total_amount = get_order_details(db, order_no)
    
        if not master:
            st.error("주문 정보를 찾을 수 없습니다.")
            st.session_state.open_order_dialog = None
            return
        
        # 마스터 정보를 딕셔너리로 변환 (세션 종료 후에도 접근 가능하도록)
        master_data = {
            "order_no": master.order_no,
            "order_date": master.order_date,
            "customer_company": master.customer_company,
            "order_type": master.order_type,
            "status": master.status,
            "priority": master.priority,
            "approved_by": master.approved_by,
            "approved_at": master.approved_at,
            "created_by": master.created_by,
            "created_at": master.created_at,
        }
        
        # 상세 정보를 딕셔너리 리스트로 변환
        details_data = []
        if details:
            for detail in details:
                details_data.append({
                    "order_seq": detail.order_seq,
                    "item_name": detail.item_name,
                    "order_qty": detail.order_qty,
                    "unit_price": float(detail.unit_price),
                    "shipping_qty": detail.shipping_qty or 0,
                    "shipping_amount": float(detail.shipping_amount) if detail.shipping_amount else 0.0,
                })
        
        # 입고 상태 정보 조회 및 변환
        receipt_status = get_detailed_receipt_status(db, order_no)
        receipt_status_data = []
        if receipt_status:
            for status in receipt_status:
                detail = status["detail"]
                receipt_status_data.append({
                    "item_name": detail.item_name,
                    "order_qty": detail.order_qty,
                    "received_qty": status["received_qty"],
                    "remaining_qty": status["remaining_qty"],
                })
        
        receipt_history = get_receipt_history(db, order_no) if receipt_status else None
        receipt_history_data = []
        if receipt_history:
            for receipt in receipt_history:
                receipt_history_data.append({
                    "received_date": receipt.received_date,
                    "item_name": receipt.item_name,
                    "received_qty": receipt.received_qty,
                    "received_by": receipt.received_by,
                })
        
        # 출하 계획/상태 정보 조회 및 변환
        shipping_plans = get_shipping_plans_for_order(db, order_no)
        shipping_plans_data = []
        plan_details_map = {}
        if shipping_plans:
            for plan in shipping_plans:
                detail = db.query(OrderDetail).filter_by(order_no=plan.order_no, order_seq=plan.order_seq).first()
                plan_details_map[(plan.order_no, plan.order_seq)] = detail.item_name if detail else "N/A"
                shipping_plans_data.append({
                    "order_no": plan.order_no,
                    "order_seq": plan.order_seq,
                    "planned_qty": plan.planned_qty,
                    "planned_shipping_date": plan.planned_shipping_date,
                    "status": plan.status,
                    "created_at": plan.created_at,
                })
        
        # 재고 상태 정보 조회 및 변환 (입고가 있는 경우)
        inventory_data_list = []
        if receipt_status:
            for status in receipt_status:
                detail = status["detail"]
                inventory = get_item_inventory_status(db, detail.order_no, detail.order_seq)
                inventory_data_list.append({
                    "item_name": detail.item_name,
                    "received": inventory["received"],
                    "planned": inventory["planned"],
                    "shipped": inventory["shipped"],
                    "available": inventory["available"],
                })
        
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.session_state.open_order_dialog = None
        return
    finally:
        # 다이얼로그를 열기 전에 db 세션 닫기
        close_db(db)
    
    # st.dialog를 사용한 모달 팝업 표시
    with st.dialog(f"📋 주문 상세보기: {order_no}"):
        _render_dialog_content(master_data, details_data, total_amount, receipt_status_data, 
                              receipt_history_data, shipping_plans_data, plan_details_map, 
                              inventory_data_list)


def _render_dialog_content(master_data, details_data, total_amount, receipt_status_data,
                          receipt_history_data, shipping_plans_data, plan_details_map,
                          inventory_data_list):
    """다이얼로그 내용을 렌더링합니다."""
    st.markdown(f"### 주문 정보")
    
    # 주문 마스터 정보
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**주문번호:** {master_data['order_no']}")
        st.markdown(f"**주문일자:** {master_data['order_date'].strftime('%Y-%m-%d')}")
        st.markdown(f"**고객사:** {master_data['customer_company']}")
        st.markdown(f"**주문구분:** {master_data['order_type']}")
    
    with col2:
        st.markdown(f"**상태:** {master_data['status']}")
        st.markdown(f"**우선순위:** {master_data['priority'] or 'N/A'}")
        if master_data['approved_by']:
            st.markdown(f"**승인자:** {master_data['approved_by']}")
            if master_data['approved_at']:
                st.markdown(f"**승인일시:** {master_data['approved_at'].strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"**등록자:** {master_data['created_by']}")
        st.markdown(f"**등록일시:** {master_data['created_at'].strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    # 총 주문금액
    st.metric("총 주문금액", f"{total_amount:,.0f}원")
    
    st.markdown("---")
    
    # 주문 상세 정보
    st.markdown("#### 주문 상세")
    if details_data:
        detail_data = []
        for detail in details_data:
            detail_data.append({
                "순번": detail["order_seq"],
                "품목명": detail["item_name"],
                "주문수량": f"{detail['order_qty']:,}",
                "단가": f"{detail['unit_price']:,.0f}원",
                "금액": f"{detail['order_qty'] * detail['unit_price']:,.0f}원",
                "출하수량": f"{detail['shipping_qty']:,}",
                "출하금액": f"{detail['shipping_amount']:,.0f}원",
            })
        
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
    else:
        st.info("주문 상세 정보가 없습니다.")
    
    # 입고 상태 정보
    if receipt_status_data:
        st.markdown("---")
        st.markdown("#### 입고 상태")
        receipt_data = []
        for status in receipt_status_data:
            receipt_data.append({
                "품목명": status["item_name"],
                "주문수량": f"{status['order_qty']:,}",
                "입고수량": f"{status['received_qty']:,}",
                "잔량": f"{status['remaining_qty']:,}",
                "진행률": f"{(status['received_qty'] / status['order_qty'] * 100):.1f}%" if status['order_qty'] > 0 else "0%"
            })
        
        receipt_df = pd.DataFrame(receipt_data)
        st.dataframe(receipt_df, use_container_width=True, hide_index=True)
        
        # 입고 내역
        if receipt_history_data:
            with st.expander("입고 내역"):
                history_data = []
                for receipt in receipt_history_data:
                    history_data.append({
                        "입고일자": receipt["received_date"].strftime("%Y-%m-%d"),
                        "품목명": receipt["item_name"],
                        "입고수량": f"{receipt['received_qty']:,}",
                        "입고자": receipt["received_by"]
                    })
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # 출하 계획/상태 정보
    if shipping_plans_data:
        st.markdown("---")
        st.markdown("#### 출하 계획/상태")
        plan_data = []
        for plan in shipping_plans_data:
            item_name = plan_details_map.get((plan["order_no"], plan["order_seq"]), "N/A")
            plan_data.append({
                "품목명": item_name,
                "출하수량": f"{plan['planned_qty']:,}",
                "출하예정일": plan["planned_shipping_date"].strftime('%Y-%m-%d') if plan["planned_shipping_date"] else "N/A",
                "상태": plan["status"],
                "등록일시": plan["created_at"].strftime('%Y-%m-%d %H:%M') if plan["created_at"] else "N/A"
            })
        
        plan_df = pd.DataFrame(plan_data)
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
    
    # 재고 상태 정보 (입고가 있는 경우)
    if inventory_data_list:
        st.markdown("---")
        st.markdown("#### 재고 상태")
        inventory_data = []
        for item in inventory_data_list:
            inventory_data.append({
                "품목명": item["item_name"],
                "입고수량": f"{item['received']:,}",
                "계획수량": f"{item['planned']:,}",
                "출하수량": f"{item['shipped']:,}",
                "가용재고": f"{item['available']:,}"
            })
        
        inventory_df = pd.DataFrame(inventory_data)
        st.dataframe(inventory_df, use_container_width=True, hide_index=True)
    
    # 닫기 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("닫기", use_container_width=True, type="primary"):
            # session_state 초기화하여 다이얼로그 닫기
            st.session_state.open_order_dialog = None
            st.rerun()


def render_order_dialog_if_needed():
    """
    페이지 레벨에서 호출하여 session_state에 저장된 주문번호가 있으면 다이얼로그를 렌더링합니다.
    각 페이지의 show_page() 함수 시작 부분에서 호출해야 합니다.
    """
    # st.dialog 사용 가능 여부 확인
    if not hasattr(st, 'dialog'):
        return
    
    check_and_render_dialog()


def show_order_detail_dialog(order_no):
    """
    주문 상세보기 다이얼로그를 표시합니다. (하위 호환성을 위한 래퍼 함수)
    
    Args:
        order_no: 주문번호
    """
    show_order_detail_modal(order_no)


def _render_order_details_simple(order_no):
    """st.dialog를 사용할 수 없을 때 사용하는 간단한 버전"""
    db = get_db()
    try:
        master, details, total_amount = get_order_details(db, order_no)
        if not master:
            st.error("주문 정보를 찾을 수 없습니다.")
            return
        
        st.markdown(f"**주문번호:** {master.order_no}")
        st.markdown(f"**주문일자:** {master.order_date.strftime('%Y-%m-%d')}")
        st.markdown(f"**고객사:** {master.customer_company}")
        st.markdown(f"**상태:** {master.status}")
        st.metric("총 주문금액", f"{total_amount:,.0f}원")
        
        if details:
            detail_data = []
            for detail in details:
                detail_data.append({
                    "순번": detail.order_seq,
                    "품목명": detail.item_name,
                    "주문수량": f"{detail.order_qty:,}",
                    "단가": f"{detail.unit_price:,.0f}원",
                    "금액": f"{detail.order_qty * detail.unit_price:,.0f}원",
                })
            detail_df = pd.DataFrame(detail_data)
            st.dataframe(detail_df, use_container_width=True, hide_index=True)
    finally:
        close_db(db)


"""
출하 등록 페이지 (발주사)
발주사가 자신의 주문에 대한 출하를 확인하고 등록하는 기능
"""
import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail, ShippingPlan
from utils.validators import validate_qty
import pandas as pd

# Streamlit 기본 페이지 네비게이션 숨김
st.markdown("""
<style>
div[data-testid="stSidebarNav"],
nav[data-testid="stSidebarNav"],
section[data-testid="stSidebarNav"],
ul[data-testid="stSidebarNav"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# 역할 확인 (발주사만 접근 가능)
require_role(["발주사"])

# 사이드바 표시
from utils.sidebar import show_sidebar
show_sidebar()

st.title("출하 등록")
st.markdown("---")

user = get_current_user()
customer_company = user.get("company_name", "")

# 상단 버튼 영역
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
with col_btn1:
    if st.button("초기화면", use_container_width=True, type="secondary"):
        st.switch_page("pages/5_대시보드.py")

st.markdown("---")

# 탭 구성
tab1, tab2 = st.tabs(["출하 계획 확인", "출하 완료 등록"])

db = get_db()
try:
    with tab1:
        st.subheader("출하 계획 확인")
        st.markdown("본사 주문에 대한 출하 계획을 확인할 수 있습니다.")
        
        # 필터 옵션
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            status_filter = st.selectbox(
                "주문 상태 필터",
                options=["전체", "승인", "생산중", "입고완료", "출하완료"],
                key="shipping_status_filter"
            )
        
        with col_filter2:
            search_order_no = st.text_input("주문번호 검색", key="search_order_no", placeholder="주문번호를 입력하세요")
        
        # 주문 조회 (발주사의 주문만)
        query = db.query(OrderMaster).filter(
            OrderMaster.customer_company == customer_company
        )
        
        if status_filter != "전체":
            query = query.filter(OrderMaster.status == status_filter)
        
        if search_order_no:
            query = query.filter(OrderMaster.order_no.like(f"%{search_order_no}%"))
        
        orders = query.order_by(OrderMaster.order_date.desc(), OrderMaster.order_no.desc()).all()
        
        if not orders:
            st.info("조회된 주문이 없습니다.")
        else:
            st.markdown(f"**조회 결과: {len(orders)}건**")
            
            for order in orders:
                with st.expander(f"**{order.order_no}** - {order.order_date.strftime('%Y-%m-%d')} ({order.status})", expanded=False):
                    # 주문 마스터 정보
                    col_master1, col_master2, col_master3 = st.columns(3)
                    with col_master1:
                        st.write(f"**주문일자:** {order.order_date.strftime('%Y-%m-%d')}")
                        st.write(f"**주문구분:** {order.order_type}")
                    with col_master2:
                        st.write(f"**상태:** {order.status}")
                        st.write(f"**우선순위:** {order.priority}")
                    with col_master3:
                        if order.approved_at:
                            st.write(f"**승인일시:** {order.approved_at.strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**승인자:** {order.approved_by}")
                    
                    # 주문 상세 및 출하 계획
                    order_details = db.query(OrderDetail).filter(
                        OrderDetail.order_no == order.order_no
                    ).order_by(OrderDetail.order_seq).all()
                    
                    if order_details:
                        st.markdown("#### 주문 상세 및 출하 계획")
                        detail_data = []
                        
                        for detail in order_details:
                            # 출하 계획 조회
                            shipping_plans = db.query(ShippingPlan).filter(
                                ShippingPlan.order_no == order.order_no,
                                ShippingPlan.order_seq == detail.order_seq
                            ).all()
                            
                            total_planned = sum(plan.planned_qty for plan in shipping_plans if plan.status == "계획")
                            total_instructed = sum(plan.planned_qty for plan in shipping_plans if plan.status == "지시")
                            total_shipped = sum(plan.planned_qty for plan in shipping_plans if plan.status == "출하완료")
                            
                            detail_data.append({
                                "순번": detail.order_seq,
                                "품목명": detail.item_name,
                                "주문수량": f"{detail.order_qty:,}",
                                "출하계획": f"{total_planned:,}",
                                "출하지시": f"{total_instructed:,}",
                                "출하완료": f"{total_shipped:,}",
                                "잔량": f"{detail.order_qty - total_shipped:,}",
                                "납품예정일": detail.planned_shipping_date.strftime("%Y-%m-%d") if detail.planned_shipping_date else "-"
                            })
                        
                        detail_df = pd.DataFrame(detail_data)
                        st.dataframe(detail_df, use_container_width=True, hide_index=True)
                        
                        # 출하 계획 상세
                        all_plans = db.query(ShippingPlan).filter(
                            ShippingPlan.order_no == order.order_no
                        ).order_by(ShippingPlan.order_seq, ShippingPlan.planned_shipping_date).all()
                        
                        if all_plans:
                            st.markdown("##### 출하 계획 상세")
                            plan_data = []
                            for plan in all_plans:
                                # 해당 순번의 상세 정보 찾기
                                plan_detail = next((d for d in order_details if d.order_seq == plan.order_seq), None)
                                plan_data.append({
                                    "순번": plan.order_seq,
                                    "품목명": plan_detail.item_name if plan_detail else "",
                                    "출하예정일": plan.planned_shipping_date.strftime("%Y-%m-%d"),
                                    "계획수량": f"{plan.planned_qty:,}",
                                    "상태": plan.status,
                                    "등록일시": plan.created_at.strftime("%Y-%m-%d %H:%M") if plan.created_at else "-"
                                })
                            plan_df = pd.DataFrame(plan_data)
                            st.dataframe(plan_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("출하 완료 등록")
        st.markdown("출하 완료된 주문을 확인하고 등록할 수 있습니다.")
        
        # 출하 지시가 있는 주문만 조회 (입고완료 또는 출하완료 상태)
        orders_with_shipping = db.query(OrderMaster).filter(
            OrderMaster.customer_company == customer_company,
            OrderMaster.status.in_(["입고완료", "출하완료"])
        ).order_by(OrderMaster.order_date.desc()).all()
        
        # 출하 지시가 있는 주문만 필터링
        orders_with_instruct = []
        for order in orders_with_shipping:
            has_instruct = db.query(ShippingPlan).filter(
                ShippingPlan.order_no == order.order_no,
                ShippingPlan.status.in_(["지시", "출하완료"])
            ).first()
            if has_instruct:
                orders_with_instruct.append(order)
        
        if not orders_with_instruct:
            st.info("출하 지시가 있는 주문이 없습니다.")
            st.markdown("""
            **출하 지시 절차:**
            1. 주문담당자가 출하 계획을 수립합니다.
            2. 주문담당자가 출하 지시를 합니다.
            3. 발주사가 출하 지시를 확인하고 수신 등록을 합니다.
            """)
        else:
            selected_order_no = st.selectbox(
                "주문 선택",
                options=["선택하세요"] + [order.order_no for order in orders_with_instruct],
                key="selected_order_for_shipping"
            )
            
            if selected_order_no != "선택하세요":
                selected_order = db.query(OrderMaster).filter(
                    OrderMaster.order_no == selected_order_no
                ).first()
                
                if selected_order:
                    st.markdown(f"**주문번호:** {selected_order_no}")
                    st.markdown(f"**주문일자:** {selected_order.order_date.strftime('%Y-%m-%d')}")
                    st.markdown(f"**상태:** {selected_order.status}")
                    
                    # 출하 계획이 있는 상세 항목 조회
                    order_details = db.query(OrderDetail).filter(
                        OrderDetail.order_no == selected_order_no
                    ).order_by(OrderDetail.order_seq).all()
                    
                    if order_details:
                        st.markdown("---")
                        st.markdown("#### 출하 완료 등록")
                        
                        shipping_items = []
                        
                        for detail in order_details:
                            # 출하 지시 조회 (지시 상태인 계획만)
                            shipping_plans = db.query(ShippingPlan).filter(
                                ShippingPlan.order_no == selected_order_no,
                                ShippingPlan.order_seq == detail.order_seq,
                                ShippingPlan.status == "지시"  # 출하 지시된 계획만
                            ).all()
                            
                            if shipping_plans:
                                for plan in shipping_plans:
                                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                                    
                                    with col1:
                                        st.markdown(f"**{detail.item_name}**")
                                        st.caption(f"출하예정일: {plan.planned_shipping_date.strftime('%Y-%m-%d')}")
                                    
                                    with col2:
                                        st.write(f"계획수량: {plan.planned_qty:,}")
                                    
                                    with col3:
                                        received_qty = st.number_input(
                                            "수신수량",
                                            min_value=0,
                                            max_value=plan.planned_qty,
                                            value=plan.planned_qty,
                                            key=f"received_{plan.plan_id}"
                                        )
                                    
                                    with col4:
                                        received_date = st.date_input(
                                            "수신일자",
                                            value=date.today(),
                                            key=f"received_date_{plan.plan_id}"
                                        )
                                    
                                    if received_qty > 0:
                                        shipping_items.append({
                                            "plan_id": plan.plan_id,
                                            "order_no": plan.order_no,
                                            "order_seq": plan.order_seq,
                                            "item_name": detail.item_name,
                                            "planned_qty": plan.planned_qty,
                                            "received_qty": received_qty,
                                            "received_date": received_date
                                        })
                                    
                                    st.markdown("---")
                        
                        if shipping_items:
                            if st.button("출하 완료 등록", use_container_width=True, type="primary", key="register_shipping"):
                                # 검증
                                errors = []
                                
                                for item in shipping_items:
                                    if item["received_qty"] <= 0:
                                        errors.append(f"{item['item_name']}: 수신수량은 1 이상이어야 합니다.")
                                
                                if errors:
                                    st.error("\n".join(errors))
                                else:
                                    # 출하 완료 처리
                                    try:
                                        for item in shipping_items:
                                            # 출하 계획 상태 변경
                                            plan = db.query(ShippingPlan).filter(
                                                ShippingPlan.plan_id == item["plan_id"]
                                            ).first()
                                            
                                            if plan:
                                                plan.status = "출하완료"
                                            
                                            # 주문 상세의 출하 수량 및 출하일자 업데이트
                                            order_detail = db.query(OrderDetail).filter(
                                                OrderDetail.order_no == item["order_no"],
                                                OrderDetail.order_seq == item["order_seq"]
                                            ).first()
                                            
                                            if order_detail:
                                                order_detail.shipping_qty = (order_detail.shipping_qty or 0) + item["received_qty"]
                                                order_detail.shipping_amount = Decimal(str(order_detail.unit_price)) * order_detail.shipping_qty
                                                if not order_detail.actual_shipping_date:
                                                    order_detail.actual_shipping_date = item["received_date"]
                                        
                                        # 모든 항목이 출하 완료되었는지 확인
                                        all_details = db.query(OrderDetail).filter(
                                            OrderDetail.order_no == selected_order_no
                                        ).all()
                                        
                                        all_shipped = all(
                                            detail.shipping_qty >= detail.order_qty 
                                            for detail in all_details
                                        )
                                        
                                        if all_shipped:
                                            selected_order.status = "출하완료"
                                        
                                        db.commit()
                                        st.success("출하 완료가 성공적으로 등록되었습니다.")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        db.rollback()
                                        st.error(f"출하 등록 중 오류 발생: {str(e)}")
                        else:
                            st.info("등록할 출하 계획이 없습니다.")
finally:
    close_db(db)


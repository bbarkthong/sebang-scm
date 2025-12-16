"""
주문 승인 페이지 (세방산업 주문담당자)
"""
import streamlit as st
from datetime import datetime
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail
from utils.validators import validate_priority
from config import PRIORITY_MIN, PRIORITY_MAX, PRIORITY_DEFAULT, ORDER_STATUS
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

# 역할 확인 (주문담당자만 접근 가능)
require_role(["주문담당자"])

# 사이드바 표시
from utils.sidebar import show_sidebar
show_sidebar()

st.title("주문 승인")
st.markdown("---")

user = get_current_user()

# 상단 버튼 영역
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
with col_btn1:
    if st.button("초기화면", use_container_width=True, type="secondary"):
        st.switch_page("pages/5_대시보드.py")

st.markdown("---")

# 필터 옵션
col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.selectbox(
        "상태 필터",
        options=["전체"] + list(ORDER_STATUS.keys()),
        key="status_filter"
    )
with col2:
    order_type_filter = st.selectbox(
        "주문구분 필터",
        options=["전체", "긴급", "일반"],
        key="order_type_filter"
    )
with col3:
    search_order_no = st.text_input("주문번호 검색", key="search_order_no")

# 주문 목록 조회
db = get_db()
try:
    query = db.query(OrderMaster).order_by(OrderMaster.created_at.desc())
    
    # 필터 적용
    if status_filter != "전체":
        query = query.filter(OrderMaster.status == status_filter)
    
    if order_type_filter != "전체":
        query = query.filter(OrderMaster.order_type == order_type_filter)
    
    if search_order_no:
        query = query.filter(OrderMaster.order_no.contains(search_order_no))
    
    orders = query.all()
    
    if not orders:
        st.info("조회된 주문이 없습니다.")
    else:
        st.markdown(f"### 주문 목록 (총 {len(orders)}건)")
        
        # 주문 목록 표시
        order_data = []
        for order in orders:
            order_data.append({
                "주문번호": order.order_no,
                "주문일자": order.order_date.strftime("%Y-%m-%d"),
                "주문구분": order.order_type,
                "고객사": order.customer_company,
                "상태": order.status,
                "우선순위": order.priority,
                "등록일시": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else ""
            })
        
        df = pd.DataFrame(order_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 주문 상세 보기 및 승인
        st.markdown("---")
        st.markdown("### 주문 상세 및 승인")
        
        selected_order_no = st.selectbox(
            "주문 선택",
            options=[order.order_no for order in orders],
            key="selected_order"
        )
        
        if selected_order_no:
            selected_order = db.query(OrderMaster).filter(OrderMaster.order_no == selected_order_no).first()
            
            if selected_order:
                # 주문 마스터 정보
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**주문번호:** {selected_order.order_no}")
                    st.markdown(f"**주문일자:** {selected_order.order_date.strftime('%Y-%m-%d')}")
                    st.markdown(f"**주문구분:** {selected_order.order_type}")
                    st.markdown(f"**고객사:** {selected_order.customer_company}")
                
                with col2:
                    st.markdown(f"**상태:** {selected_order.status}")
                    st.markdown(f"**우선순위:** {selected_order.priority}")
                    if selected_order.approved_by:
                        st.markdown(f"**승인자:** {selected_order.approved_by}")
                        st.markdown(f"**승인일시:** {selected_order.approved_at.strftime('%Y-%m-%d %H:%M') if selected_order.approved_at else ''}")
                    st.markdown(f"**등록자:** {selected_order.created_by}")
                
                # 주문 상세 정보
                st.markdown("#### 주문 상세")
                order_details = db.query(OrderDetail).filter(
                    OrderDetail.order_no == selected_order_no
                ).order_by(OrderDetail.order_seq).all()
                
                if order_details:
                    detail_data = []
                    total_amount = 0
                    for detail in order_details:
                        amount = float(detail.order_qty * detail.unit_price)
                        total_amount += amount
                        detail_data.append({
                            "순번": detail.order_seq,
                            "품목명": detail.item_name,
                            "주문수량": f"{detail.order_qty:,}",
                            "단가": f"{float(detail.unit_price):,.0f}",
                            "금액": f"{amount:,.0f}",
                            "납품예정일": detail.planned_shipping_date.strftime("%Y-%m-%d") if detail.planned_shipping_date else ""
                        })
                    
                    detail_df = pd.DataFrame(detail_data)
                    st.dataframe(detail_df, use_container_width=True, hide_index=True)
                    st.markdown(f"**총 주문금액:** {total_amount:,.0f}원")
                
                # 승인/거부 폼
                if selected_order.status == "대기":
                    st.markdown("---")
                    st.markdown("### 주문 승인/거부")
                    
                    with st.form("approval_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            priority = st.number_input(
                                "우선순위",
                                min_value=PRIORITY_MIN,
                                max_value=PRIORITY_MAX,
                                value=selected_order.priority or PRIORITY_DEFAULT,
                                help=f"{PRIORITY_MIN}~{PRIORITY_MAX} 사이의 값을 입력하세요."
                            )
                        
                        with col2:
                            action = st.radio(
                                "처리",
                                options=["승인", "거부"],
                                horizontal=True
                            )
                        
                        submit_approval = st.form_submit_button("처리", use_container_width=True, type="primary")
                        
                        if submit_approval:
                            # 우선순위 검증
                            is_valid, msg = validate_priority(priority)
                            if not is_valid:
                                st.error(msg)
                            else:
                                if action == "승인":
                                    selected_order.status = "승인"
                                    selected_order.priority = priority
                                    selected_order.approved_by = user["username"]
                                    selected_order.approved_at = datetime.now()
                                    
                                    db.commit()
                                    st.success(f"주문이 승인되었습니다. (우선순위: {priority})")
                                    st.rerun()
                                else:
                                    # 거부 처리 (주문 삭제 또는 상태 변경)
                                    selected_order.status = "거부"
                                    db.commit()
                                    st.success("주문이 거부되었습니다.")
                                    st.rerun()
                else:
                    st.info(f"이 주문은 이미 '{selected_order.status}' 상태입니다.")
                    
                    # 상태 변경 (승인 -> 생산중 등)
                    if selected_order.status == "승인":
                        st.markdown("---")
                        if st.button("생산중으로 상태 변경", type="primary"):
                            selected_order.status = "생산중"
                            db.commit()
                            st.success("상태가 변경되었습니다.")
                            st.rerun()
except Exception as e:
    st.error(f"오류 발생: {str(e)}")
finally:
    close_db(db)


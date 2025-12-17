
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from auth.auth import get_current_user
from database.connection import get_db, close_db
from utils.excel_handler import download_template
from utils.validators import validate_order_date, validate_order_type, validate_customer_company, validate_qty
from config import ORDER_TYPE
from services.order_service import get_active_items, create_order, process_excel_file

def show_page():
    """Renders the Order Registration page."""
    st.title("주문 등록")
    st.markdown("---")

    user = get_current_user()

    if "order_reg_state" not in st.session_state:
        st.session_state.order_reg_state = {"order_details": []}
    
    page_state = st.session_state.order_reg_state

    tab1, tab2 = st.tabs(["수동 주문 등록", "엑셀 업로드"])

    db = get_db()
    try:
        with tab1:
            render_manual_order_tab(db, user, page_state)
        with tab2:
            render_excel_upload_tab(db, user)
    finally:
        close_db(db)

def render_manual_order_tab(db, user, page_state):
    """Renders the manual order registration tab."""
    st.subheader("수동 주문 등록")

    # Order Master Info
    col1, col2, col3 = st.columns(3)
    order_date = col1.date_input("주문일자 *", date.today(), key="man_order_date")
    customer_company = col2.text_input("고객사 *", user.get("company_name", ""), key="man_customer")
    order_type = col3.selectbox("주문구분 *", list(ORDER_TYPE.keys()), key="man_order_type")
    
    col1.caption(f"**등록일시:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    col2.caption(f"**등록자:** {user.get('username', '')}")
    
    # Add Item Section
    items = get_active_items(db)
    item_dict = {item.item_name: item for item in items}
    render_add_detail_section(item_dict, order_date, page_state)

    if page_state["order_details"]:
        render_order_details_list(page_state)
        render_create_order_form(db, user, page_state, {
            "order_date": order_date, "customer_company": customer_company, "order_type": order_type
        })
    else:
        st.info("주문 상세 항목을 추가해주세요.")

def render_add_detail_section(item_dict, order_date, page_state):
    """Renders the section for adding a new order detail item."""
    st.markdown("### 주문 상세 항목 추가")
    with st.expander("항목 추가", expanded=True):
        cols = st.columns(3)
        item_names = ["선택하세요"] + list(item_dict.keys())
        selected_name = cols[0].selectbox("품목명 *", item_names)
        
        item, qty = None, 1
        if selected_name != "선택하세요":
            item = item_dict[selected_name]
            cols[0].text_input("단가", f"{float(item.unit_price):,.0f}원", disabled=True)
            min_date = order_date + timedelta(days=item.lead_time_days) if item.lead_time_days > 0 else order_date
            qty = cols[1].number_input("주문수량 *", 1, value=1)
            ship_date = cols[1].date_input("납품예정일", min_date, min_value=min_date)
        cols[2].caption(f"")

        if cols[2].button("항목 추가", use_container_width=True, type="primary"):
            if not item:
                st.error("품목을 선택해주세요.")
            else:
                page_state["order_details"].append({
                    "item_code": item.item_code, "item_name": item.item_name, "order_qty": int(qty),
                    "unit_price": float(item.unit_price), "planned_shipping_date": ship_date
                })
                st.rerun()

def render_order_details_list(page_state):
    """Displays the interactive list of added order details."""
    st.markdown("#### 등록된 주문 상세")
    
    if not page_state["order_details"]:
        return
    
    # Header
    header_cols = st.columns([1, 2, 1, 1, 1, 1])
    with header_cols[0]:
        st.write("**순번**")
    with header_cols[1]:
        st.write("**품목명**")
    with header_cols[2]:
        st.write("**주문수량**")
    with header_cols[3]:
        st.write("**단가**")
    with header_cols[4]:
        st.write("**납품예정일**")
    with header_cols[5]:
        st.write("**삭제**")
    
    st.markdown("---")
    
    # Details rows
    for idx, detail in enumerate(page_state["order_details"]):
        detail_cols = st.columns([1, 2, 1, 1, 1, 1])
        
        with detail_cols[0]:
            st.write(f"{idx + 1}")
        with detail_cols[1]:
            st.write(detail['item_name'])
        with detail_cols[2]:
            st.write(f"{detail['order_qty']:,}개")
        with detail_cols[3]:
            st.write(f"{detail['unit_price']:,.0f}원")
        with detail_cols[4]:
            st.write(detail["planned_shipping_date"].strftime("%Y-%m-%d") if detail.get("planned_shipping_date") else "-")
        with detail_cols[5]:
            if st.button("삭제", key=f"delete_{idx}", type="secondary"):
                page_state["order_details"].pop(idx)
                st.rerun()
    
    st.markdown("---")
    
    if st.button("전체 삭제", type="secondary", key="clear_all_details"):
        page_state["order_details"] = []
        st.rerun()

def render_create_order_form(db, user, page_state, order_data):
    """Renders the final submission form for a manual order."""
    st.markdown("### 발주서 생성")
    with st.form("manual_order_form"):
        if st.form_submit_button("📄 발주서 생성 및 등록", use_container_width=True, type="primary"):
            try:
                order_no = create_order(db, user, order_data, page_state["order_details"])
                st.success(f"주문이 성공적으로 등록되었습니다. (주문번호: {order_no})")
                page_state["order_details"] = []
                st.rerun()
            except Exception as e:
                st.error(f"주문 등록 중 오류: {e}")

def render_excel_upload_tab(db, user):
    """Renders the Excel upload tab."""
    st.subheader("엑셀 업로드")
    
    st.download_button("주문 템플릿 다운로드", download_template(), "주문템플릿.xlsx")
    
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=['xlsx', 'xls'])
    if not uploaded_file:
        return

    success, details, error_msg = process_excel_file(uploaded_file)
    if not success:
        st.error(f"엑셀 처리 실패: {error_msg}")
        return
        
    st.success(f"{len(details)}개 항목을 읽었습니다.")
    st.dataframe(pd.DataFrame(details))

    with st.form("excel_order_form"):
        st.markdown("### 주문 정보 입력")
        col1, col2, col3 = st.columns(3)
        order_date = col1.date_input("주문일자 *", date.today(), key="excel_order_date")
        customer_company = col2.text_input("고객사 *", user.get("company_name", ""), key="excel_customer")
        order_type = col3.selectbox("주문구분 *", list(ORDER_TYPE.keys()), key="excel_order_type")

        col1.caption(f"**등록일시:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        col2.caption(f"**등록자:** {user.get('username', '')}")

        if st.form_submit_button("주문 등록", use_container_width=True, type="primary"):
            try:
                order_no = create_order(db, user, {
                    "order_date": order_date, "order_type": order_type, "customer_company": customer_company
                }, details)
                st.success(f"주문이 성공적으로 등록되었습니다. (주문번호: {order_no})")
                st.rerun()
            except Exception as e:
                st.error(f"주문 등록 중 오류: {e}")

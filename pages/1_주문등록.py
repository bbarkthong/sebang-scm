"""
주문 등록 페이지 (발주사)
"""
import streamlit as st
from datetime import datetime, date
from decimal import Decimal
import uuid
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail, ItemMaster
from utils.excel_handler import parse_excel_file, download_template
from utils.order_utils import generate_order_no
from utils.validators import (
    validate_order_date, validate_order_type,
    validate_customer_company, validate_item_name,
    validate_qty, validate_unit_price
)
from config import ORDER_TYPE
from datetime import timedelta

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

st.title("주문 등록")
st.markdown("---")

user = get_current_user()

# 탭 구성
tab1, tab2 = st.tabs(["수동 주문 등록", "엑셀 업로드"])

with tab1:
    st.subheader("수동 주문 등록")
    
    # 주문 상세 항목 입력 (form 밖에서 관리)
    if "order_details" not in st.session_state:
        st.session_state.order_details = []
    
    # 주문 정보 입력 (이미지 참고: 상단에 주요 정보 배치)
    st.markdown("### 주문 정보")
    
    # 상단 버튼 영역 (이미지 참고: 상단 버튼들)
    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
    with col_btn1:
        if st.button("초기화면", use_container_width=True, type="secondary"):
            st.switch_page("pages/5_대시보드.py")
    
    st.markdown("---")
    
    # 주문 기본 정보
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        order_date = st.date_input("주문일자 *", value=date.today(), key="order_date_input")
        # 주문번호 자동 생성
        if "auto_order_no" not in st.session_state or st.session_state.get("last_order_date") != order_date:
            order_no = generate_order_no(order_date)
            st.session_state.auto_order_no = order_no
            st.session_state.last_order_date = order_date
        else:
            order_no = st.session_state.auto_order_no
        st.text_input("주문번호 *", value=order_no, disabled=True, help="주문번호는 자동으로 생성됩니다.")
    
    with col_info2:
        customer_company = st.text_input("고객사 *", value=user.get("company_name", ""), key="customer_company_input")
        order_type = st.selectbox("주문구분 *", options=list(ORDER_TYPE.keys()), key="order_type_input_preview")
    
    with col_info3:
        st.markdown("<br>", unsafe_allow_html=True)  # 공간 맞추기
        st.caption(f"**등록자:** {user.get('username', '')}")
        st.caption(f"**등록일시:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 품목 마스터 조회
    db = get_db()
    try:
        items = db.query(ItemMaster).filter(ItemMaster.is_active == "Y").order_by(ItemMaster.item_name).all()
        item_dict = {item.item_name: item for item in items}
        item_names = list(item_dict.keys())
    finally:
        close_db(db)
    
    if not item_names:
        st.warning("등록된 품목이 없습니다. 관리자에게 문의하세요.")
    else:
        # 주문 상세 추가 섹션 (form 밖)
        st.markdown("### 주문 상세 항목 추가")
        with st.expander("주문 상세 항목 추가", expanded=True):
            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
            
            with detail_col1:
                selected_item_name = st.selectbox("품목명 *", options=["선택하세요"] + item_names, key="detail_item_name")
                if selected_item_name != "선택하세요":
                    selected_item = item_dict[selected_item_name]
                    # 품목코드는 내부적으로만 사용 (UI에 표시하지 않음)
                    item_code = selected_item.item_code
                    unit_price = float(selected_item.unit_price)  # 품목 마스터의 단가 사용
                    lead_time_days = selected_item.lead_time_days
                else:
                    item_code = None
                    unit_price = 0.0
                    lead_time_days = 0
            
            with detail_col2:
                order_qty = st.number_input("주문수량 *", min_value=1, value=1, key="detail_qty")
                # 단가는 품목 마스터에서 관리되므로 읽기 전용으로 표시
                if selected_item_name != "선택하세요":
                    st.text_input("단가 *", value=f"{unit_price:,.0f}원", disabled=True, help="단가는 품목 마스터에서 관리됩니다.")
                else:
                    st.text_input("단가 *", value="품목을 선택하세요", disabled=True)
            
            with detail_col3:
                # 주문일자 기준으로 납기일 계산
                if selected_item_name != "선택하세요" and lead_time_days > 0:
                    min_date = order_date + timedelta(days=lead_time_days)
                    planned_shipping_date = st.date_input(
                        "납품예정일",
                        value=min_date,
                        min_value=min_date,
                        key="detail_shipping_date",
                        help=f"주문일자 기준 최소 {lead_time_days}일 후 선택 가능"
                    )
                else:
                    planned_shipping_date = st.date_input("납품예정일", key="detail_shipping_date", min_value=order_date)
            
            with detail_col4:
                st.write("")  # 공간 맞추기
                st.write("")
                add_detail_btn = st.button("항목 추가", use_container_width=True, type="primary")
            
            if add_detail_btn:
                # 검증
                errors = []
                
                if selected_item_name == "선택하세요" or not selected_item_name:
                    errors.append("품목명을 선택해주세요.")
                else:
                    # 품목 선택 시 품목 정보 다시 가져오기
                    selected_item = item_dict[selected_item_name]
                    item_code = selected_item.item_code
                    unit_price = float(selected_item.unit_price)
                
                if not errors:
                    is_valid, msg = validate_qty(order_qty)
                    if not is_valid:
                        errors.append(f"주문수량: {msg}")
                
                if errors:
                    st.error("\n".join(errors))
                else:
                    detail = {
                        "item_code": item_code,
                        "item_name": selected_item_name,
                        "order_qty": int(order_qty),
                        "unit_price": unit_price,
                        "planned_shipping_date": planned_shipping_date
                    }
                    st.session_state.order_details.append(detail)
                    st.success("항목이 추가되었습니다.")
                    # 입력 필드 초기화를 위해 rerun
                    st.rerun()
        
        # 주문 상세 목록 표시 (1 row씩 표시)
        if st.session_state.order_details:
            st.markdown("#### 등록된 주문 상세")
            
            # 헤더
            header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 2, 1, 1, 1, 1])
            with header_col1:
                st.write("**순번**")
            with header_col2:
                st.write("**품목명**")
            with header_col3:
                st.write("**주문수량**")
            with header_col4:
                st.write("**단가**")
            with header_col5:
                st.write("**납품예정일**")
            with header_col6:
                st.write("**삭제**")
            
            st.markdown("---")
            
            # 각 항목을 1 row씩 표시
            for idx, detail in enumerate(st.session_state.order_details):
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"{idx + 1}")
                
                with col2:
                    st.write(detail['item_name'])
                
                with col3:
                    st.write(f"{detail['order_qty']:,}개")
                
                with col4:
                    st.write(f"{detail['unit_price']:,.0f}원")
                
                with col5:
                    st.write(detail["planned_shipping_date"].strftime("%Y-%m-%d") if detail["planned_shipping_date"] else "-")
                
                with col6:
                    if st.button("삭제", key=f"delete_{idx}", type="secondary"):
                        st.session_state.order_details.pop(idx)
                        st.rerun()
            
            st.markdown("---")
            
            if st.button("전체 삭제", type="secondary", key="clear_all_details"):
                st.session_state.order_details = []
                st.rerun()
        
        # 주문 등록 폼 (항목 추가 후 발주서 생성)
        if st.session_state.order_details:
            st.markdown("---")
            st.markdown("### 발주서 생성")
            
            # 주문 요약 정보 표시 (이미지 참고: 상단에 요약 정보)
            total_qty = sum(detail["order_qty"] for detail in st.session_state.order_details)
            total_amount = sum(detail["order_qty"] * detail["unit_price"] for detail in st.session_state.order_details)
            
            col_summary1, col_summary2, col_summary3 = st.columns(3)
            with col_summary1:
                st.metric("총 품목 수", f"{len(st.session_state.order_details)}개")
            with col_summary2:
                st.metric("총 주문 수량", f"{total_qty:,}개")
            with col_summary3:
                st.metric("총 주문 금액", f"{total_amount:,.0f}원")
            
            with st.form("manual_order_form"):
                submit_button = st.form_submit_button("📄 발주서 생성 및 등록", use_container_width=True, type="primary")
                
                if submit_button:
                    # 검증
                    errors = []
                    
                    # order_type은 이미 위에서 선택됨
                    order_type = st.session_state.get("order_type_input_preview", list(ORDER_TYPE.keys())[0])
                    
                    is_valid, msg = validate_order_date(order_date)
                    if not is_valid:
                        errors.append(f"주문일자: {msg}")
                    
                    is_valid, msg = validate_order_type(order_type)
                    if not is_valid:
                        errors.append(f"주문구분: {msg}")
                    
                    is_valid, msg = validate_customer_company(customer_company)
                    if not is_valid:
                        errors.append(f"고객사: {msg}")
                    
                    if not st.session_state.order_details:
                        errors.append("주문 상세 항목을 최소 1개 이상 추가해주세요.")
                    
                    if errors:
                        st.error("\n".join(errors))
                    else:
                        # 주문번호 재생성 (최신 번호로)
                        order_no = generate_order_no(order_date)
                        
                        # DB 저장
                        db = get_db()
                        try:
                            # 주문 마스터 저장
                            order_master = OrderMaster(
                                order_no=order_no,
                                order_date=order_date,
                                order_type=order_type,
                                customer_company=customer_company,
                                status="대기",
                                created_by=user["username"]
                            )
                            db.add(order_master)
                            
                            # 주문 상세 저장
                            for idx, detail in enumerate(st.session_state.order_details):
                                order_detail = OrderDetail(
                                    order_no=order_no,
                                    order_seq=idx + 1,
                                    item_code=detail["item_code"],
                                    item_name=detail["item_name"],
                                    order_qty=detail["order_qty"],
                                    unit_price=Decimal(str(detail["unit_price"])),
                                    planned_shipping_date=detail["planned_shipping_date"]
                                )
                                db.add(order_detail)
                            
                            db.commit()
                            st.success(f"주문이 성공적으로 등록되었습니다. (주문번호: {order_no})")
                            st.session_state.order_details = []
                            # 주문번호 재생성을 위해 세션 상태 초기화
                            if "auto_order_no" in st.session_state:
                                del st.session_state.auto_order_no
                            if "last_order_date" in st.session_state:
                                del st.session_state.last_order_date
                            st.rerun()
                            
                        except Exception as e:
                            db.rollback()
                            st.error(f"주문 등록 중 오류 발생: {str(e)}")
                        finally:
                            close_db(db)
        else:
            st.info("주문 상세 항목을 추가한 후 주문 등록 버튼을 눌러주세요.")

with tab2:
    st.subheader("엑셀 업로드")
    
    # 템플릿 다운로드
    st.markdown("### 1. 템플릿 다운로드")
    template_bytes = download_template()
    st.download_button(
        label="주문 템플릿 다운로드",
        data=template_bytes,
        file_name=f"주문템플릿_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("### 2. 엑셀 파일 업로드")
    uploaded_file = st.file_uploader(
        "엑셀 파일을 선택하세요",
        type=['xlsx', 'xls'],
        help="템플릿 형식에 맞춰 작성한 엑셀 파일을 업로드하세요."
    )
    
    if uploaded_file is not None:
        # 엑셀 파싱
        success, order_details, error_msg = parse_excel_file(uploaded_file)
        
        if success:
            st.success(f"{len(order_details)}개의 주문 상세 항목을 읽었습니다.")
            
            # 미리보기 (품목코드는 표시하지 않음)
            import pandas as pd
            preview_data = []
            for detail in order_details:
                preview_data.append({
                    "품목명": detail["item_name"],
                    "주문수량": detail["order_qty"],
                    "단가": f"{detail['unit_price']:,.0f}",
                    "납품예정일": detail["planned_shipping_date"].strftime("%Y-%m-%d") if detail["planned_shipping_date"] else ""
                })
            preview_df = pd.DataFrame(preview_data)
            st.dataframe(preview_df, use_container_width=True)
            
            if error_msg:
                st.warning(error_msg)
            
            # 주문 마스터 정보 입력
            st.markdown("### 3. 주문 정보 입력")
            with st.form("excel_order_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # 주문번호 자동 생성
                    excel_order_date = st.date_input("주문일자 *", value=date.today(), key="excel_order_date")
                    if "excel_auto_order_no" not in st.session_state or st.session_state.get("excel_last_order_date") != excel_order_date:
                        excel_order_no = generate_order_no(excel_order_date)
                        st.session_state.excel_auto_order_no = excel_order_no
                        st.session_state.excel_last_order_date = excel_order_date
                    else:
                        excel_order_no = st.session_state.excel_auto_order_no
                    
                    st.text_input("주문번호 *", value=excel_order_no, disabled=True, key="excel_order_no_display", help="주문번호는 자동으로 생성됩니다.")
                    excel_order_type = st.selectbox("주문구분 *", options=list(ORDER_TYPE.keys()), key="excel_order_type")
                
                with col2:
                    excel_customer_company = st.text_input("고객사 *", value=user.get("company_name", ""), key="excel_customer")
                
                excel_submit = st.form_submit_button("주문 등록", use_container_width=True, type="primary")
                
                if excel_submit:
                    # 검증
                    errors = []
                    
                    is_valid, msg = validate_order_date(excel_order_date)
                    if not is_valid:
                        errors.append(f"주문일자: {msg}")
                    
                    is_valid, msg = validate_order_type(excel_order_type)
                    if not is_valid:
                        errors.append(f"주문구분: {msg}")
                    
                    is_valid, msg = validate_customer_company(excel_customer_company)
                    if not is_valid:
                        errors.append(f"고객사: {msg}")
                    
                    if errors:
                        st.error("\n".join(errors))
                    else:
                        # 주문번호 재생성 (최신 번호로)
                        excel_order_no = generate_order_no(excel_order_date)
                        
                        # DB 저장
                        db = get_db()
                        try:
                            # 주문 마스터 저장
                            order_master = OrderMaster(
                                order_no=excel_order_no,
                                order_date=excel_order_date,
                                order_type=excel_order_type,
                                customer_company=excel_customer_company,
                                status="대기",
                                created_by=user["username"]
                            )
                            db.add(order_master)
                            
                            # 주문 상세 저장
                            for idx, detail in enumerate(order_details):
                                order_detail = OrderDetail(
                                    order_no=excel_order_no,
                                    order_seq=idx + 1,
                                    item_code=detail["item_code"],
                                    item_name=detail["item_name"],
                                    order_qty=detail["order_qty"],
                                    unit_price=Decimal(str(detail["unit_price"])),
                                    planned_shipping_date=detail["planned_shipping_date"]
                                )
                                db.add(order_detail)
                            
                            db.commit()
                            st.success(f"주문이 성공적으로 등록되었습니다. (주문번호: {excel_order_no})")
                            # 주문번호 재생성을 위해 세션 상태 초기화
                            if "excel_auto_order_no" in st.session_state:
                                del st.session_state.excel_auto_order_no
                            if "excel_last_order_date" in st.session_state:
                                del st.session_state.excel_last_order_date
                            st.rerun()
                            
                        except Exception as e:
                            db.rollback()
                            st.error(f"주문 등록 중 오류 발생: {str(e)}")
                        finally:
                            close_db(db)
        else:
            st.error(f"엑셀 파일 처리 실패: {error_msg}")


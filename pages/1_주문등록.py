"""
주문 등록 페이지 (발주사)
"""
import streamlit as st
from datetime import datetime, date
from decimal import Decimal
import uuid
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail
from utils.excel_handler import parse_excel_file, download_template
from utils.validators import (
    validate_order_no, validate_order_date, validate_order_type,
    validate_customer_company, validate_item_code, validate_item_name,
    validate_qty, validate_unit_price
)
from config import ORDER_TYPE

# 역할 확인 (발주사만 접근 가능)
require_role(["발주사"])

st.title("주문 등록")
st.markdown("---")

user = get_current_user()

# 탭 구성
tab1, tab2 = st.tabs(["수동 주문 등록", "엑셀 업로드"])

with tab1:
    st.subheader("수동 주문 등록")
    
    with st.form("manual_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            order_no = st.text_input("주문번호 *", placeholder="예: ORD-2024-001")
            order_date = st.date_input("주문일자 *", value=date.today())
            order_type = st.selectbox("주문구분 *", options=list(ORDER_TYPE.keys()))
        
        with col2:
            customer_company = st.text_input("고객사 *", value=user.get("company_name", ""))
        
        st.markdown("### 주문 상세")
        
        # 주문 상세 항목 입력
        if "order_details" not in st.session_state:
            st.session_state.order_details = []
        
        # 주문 상세 추가 폼
        with st.expander("주문 상세 항목 추가", expanded=True):
            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
            
            with detail_col1:
                item_code = st.text_input("품목코드", key="detail_item_code")
                item_name = st.text_input("품목명", key="detail_item_name")
            
            with detail_col2:
                order_qty = st.number_input("주문수량", min_value=1, value=1, key="detail_qty")
                unit_price = st.number_input("단가", min_value=0.0, value=0.0, step=0.01, key="detail_price")
            
            with detail_col3:
                planned_shipping_date = st.date_input("출하예정일", key="detail_shipping_date")
            
            with detail_col4:
                st.write("")  # 공간 맞추기
                st.write("")
                add_detail_btn = st.button("항목 추가", use_container_width=True)
            
            if add_detail_btn:
                # 검증
                errors = []
                is_valid, msg = validate_item_code(item_code)
                if not is_valid:
                    errors.append(f"품목코드: {msg}")
                
                is_valid, msg = validate_item_name(item_name)
                if not is_valid:
                    errors.append(f"품목명: {msg}")
                
                is_valid, msg = validate_qty(order_qty)
                if not is_valid:
                    errors.append(f"주문수량: {msg}")
                
                is_valid, msg = validate_unit_price(Decimal(str(unit_price)))
                if not is_valid:
                    errors.append(f"단가: {msg}")
                
                if errors:
                    st.error("\n".join(errors))
                else:
                    detail = {
                        "item_code": item_code,
                        "item_name": item_name,
                        "order_qty": int(order_qty),
                        "unit_price": float(unit_price),
                        "planned_shipping_date": planned_shipping_date
                    }
                    st.session_state.order_details.append(detail)
                    st.success("항목이 추가되었습니다.")
                    st.rerun()
        
        # 주문 상세 목록 표시
        if st.session_state.order_details:
            st.markdown("#### 등록된 주문 상세")
            detail_df_data = []
            for idx, detail in enumerate(st.session_state.order_details):
                detail_df_data.append({
                    "순번": idx + 1,
                    "품목코드": detail["item_code"],
                    "품목명": detail["item_name"],
                    "주문수량": detail["order_qty"],
                    "단가": f"{detail['unit_price']:,.0f}",
                    "출하예정일": detail["planned_shipping_date"].strftime("%Y-%m-%d") if detail["planned_shipping_date"] else ""
                })
            
            import pandas as pd
            detail_df = pd.DataFrame(detail_df_data)
            st.dataframe(detail_df, use_container_width=True)
            
            if st.button("전체 삭제", type="secondary"):
                st.session_state.order_details = []
                st.rerun()
        
        submit_button = st.form_submit_button("주문 등록", use_container_width=True, type="primary")
        
        if submit_button:
            # 검증
            errors = []
            
            is_valid, msg = validate_order_no(order_no)
            if not is_valid:
                errors.append(f"주문번호: {msg}")
            
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
                    st.rerun()
                    
                except Exception as e:
                    db.rollback()
                    st.error(f"주문 등록 중 오류 발생: {str(e)}")
                finally:
                    close_db(db)

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
            
            # 미리보기
            import pandas as pd
            preview_data = []
            for detail in order_details:
                preview_data.append({
                    "품목코드": detail["item_code"],
                    "품목명": detail["item_name"],
                    "주문수량": detail["order_qty"],
                    "단가": f"{detail['unit_price']:,.0f}",
                    "출하예정일": detail["planned_shipping_date"].strftime("%Y-%m-%d") if detail["planned_shipping_date"] else ""
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
                    excel_order_no = st.text_input("주문번호 *", placeholder="예: ORD-2024-001", key="excel_order_no")
                    excel_order_date = st.date_input("주문일자 *", value=date.today(), key="excel_order_date")
                    excel_order_type = st.selectbox("주문구분 *", options=list(ORDER_TYPE.keys()), key="excel_order_type")
                
                with col2:
                    excel_customer_company = st.text_input("고객사 *", value=user.get("company_name", ""), key="excel_customer")
                
                excel_submit = st.form_submit_button("주문 등록", use_container_width=True, type="primary")
                
                if excel_submit:
                    # 검증
                    errors = []
                    
                    is_valid, msg = validate_order_no(excel_order_no)
                    if not is_valid:
                        errors.append(f"주문번호: {msg}")
                    
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
                            st.rerun()
                            
                        except Exception as e:
                            db.rollback()
                            st.error(f"주문 등록 중 오류 발생: {str(e)}")
                        finally:
                            close_db(db)
        else:
            st.error(f"엑셀 파일 처리 실패: {error_msg}")


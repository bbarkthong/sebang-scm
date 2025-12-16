"""
입고 등록 페이지 (세방리튬배터리 제조담당자)
"""
import streamlit as st
from datetime import date, datetime
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail, Warehouse
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

# 역할 확인 (제조담당자만 접근 가능)
require_role(["제조담당자"])

# 사이드바 표시
from utils.sidebar import show_sidebar
show_sidebar()

st.title("입고 등록")
st.markdown("---")

user = get_current_user()

# 승인된 주문 또는 생산중인 주문 조회
db = get_db()
try:
    # 승인 또는 생산중 상태의 주문 조회
    orders = db.query(OrderMaster).filter(
        OrderMaster.status.in_(["승인", "생산중"])
    ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
    
    if not orders:
        st.info("입고 등록 가능한 주문이 없습니다.")
        st.markdown("""
        **입고 등록 절차:**
        1. 주문담당자가 주문을 승인해야 합니다.
        2. 승인된 주문에 대해 생산 완료 후 입고 등록을 합니다.
        3. 모든 항목이 입고 완료되면 주문 상태가 자동으로 '입고완료'로 변경됩니다.
        """)
    else:
        st.markdown(f"### 입고 등록 가능 주문 (총 {len(orders)}건)")
        st.markdown("""
        **입고 등록 방법:**
        1. 아래 목록에서 입고할 주문을 선택합니다.
        2. 각 품목의 입고수량과 입고일자를 입력합니다.
        3. '입고 등록' 버튼을 클릭합니다.
        4. 모든 항목이 입고 완료되면 주문 상태가 자동으로 '입고완료'로 변경됩니다.
        """)
        
        # 주문 목록 표시
        order_data = []
        for order in orders:
            # 각 주문의 입고 진행률 계산
            order_details = db.query(OrderDetail).filter(
                OrderDetail.order_no == order.order_no
            ).all()
            
            total_qty = sum(detail.order_qty for detail in order_details)
            total_received = 0
            for detail in order_details:
                receipts = db.query(Warehouse).filter(
                    Warehouse.order_no == order.order_no,
                    Warehouse.order_seq == detail.order_seq
                ).all()
                total_received += sum(r.received_qty for r in receipts)
            
            progress = (total_received / total_qty * 100) if total_qty > 0 else 0
            
            order_data.append({
                "주문번호": order.order_no,
                "주문일자": order.order_date.strftime("%Y-%m-%d"),
                "주문구분": order.order_type,
                "고객사": order.customer_company,
                "상태": order.status,
                "우선순위": order.priority,
                "입고진행률": f"{progress:.1f}% ({total_received:,}/{total_qty:,})"
            })
        
        df = pd.DataFrame(order_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 입고 등록")
        
        # 주문 선택
        selected_order_no = st.selectbox(
            "주문 선택",
            options=[order.order_no for order in orders],
            key="selected_order"
        )
        
        if selected_order_no:
            selected_order = db.query(OrderMaster).filter(
                OrderMaster.order_no == selected_order_no
            ).first()
            
            if selected_order:
                st.markdown(f"**선택된 주문:** {selected_order_no} ({selected_order.customer_company})")
                
                # 주문 상세 조회
                order_details = db.query(OrderDetail).filter(
                    OrderDetail.order_no == selected_order_no
                ).order_by(OrderDetail.order_seq).all()
                
                if order_details:
                    # 기존 입고 내역 조회
                    existing_receipts = db.query(Warehouse).filter(
                        Warehouse.order_no == selected_order_no
                    ).all()
                    
                    # 품목별 입고 수량 집계
                    receipt_summary = {}
                    for receipt in existing_receipts:
                        key = (receipt.order_no, receipt.order_seq)
                        if key not in receipt_summary:
                            receipt_summary[key] = 0
                        receipt_summary[key] += receipt.received_qty
                    
                    # 입고 등록 폼
                    with st.form("warehouse_form"):
                        st.markdown("#### 입고 항목 입력")
                        
                        receipt_items = []
                        for detail in order_details:
                            key = (detail.order_no, detail.order_seq)
                            received_qty = receipt_summary.get(key, 0)
                            remaining_qty = detail.order_qty - received_qty
                            
                            if remaining_qty > 0:
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.markdown(f"**{detail.item_name}**")
                                
                                with col2:
                                    st.markdown(f"주문수량: {detail.order_qty:,}")
                                    st.caption(f"입고완료: {received_qty:,} / 잔량: {remaining_qty:,}")
                                
                                with col3:
                                    received_qty_input = st.number_input(
                                        "입고수량",
                                        min_value=0,
                                        max_value=remaining_qty,
                                        value=remaining_qty,
                                        key=f"received_qty_{detail.order_no}_{detail.order_seq}"
                                    )
                                
                                with col4:
                                    received_date_input = st.date_input(
                                        "입고일자",
                                        value=date.today(),
                                        key=f"received_date_{detail.order_no}_{detail.order_seq}"
                                    )
                                
                                if received_qty_input > 0:
                                    receipt_items.append({
                                        "order_no": detail.order_no,
                                        "order_seq": detail.order_seq,
                                        "item_code": detail.item_code,
                                        "item_name": detail.item_name,
                                        "received_qty": received_qty_input,
                                        "received_date": received_date_input
                                    })
                                
                                st.markdown("---")
                        
                        if not receipt_items:
                            st.info("입고할 항목이 없습니다. (모든 항목이 이미 입고 완료되었습니다.)")
                        
                        submit_button = st.form_submit_button("입고 등록", use_container_width=True, type="primary")
                        
                        if submit_button:
                            if not receipt_items:
                                st.warning("입고할 항목을 선택해주세요.")
                            else:
                                # 입고 등록
                                try:
                                    # 입고 항목 등록
                                    for item in receipt_items:
                                        warehouse = Warehouse(
                                            order_no=item["order_no"],
                                            order_seq=item["order_seq"],
                                            item_code=item["item_code"],
                                            item_name=item["item_name"],
                                            received_qty=item["received_qty"],
                                            received_date=item["received_date"],
                                            received_by=user["username"]
                                        )
                                        db.add(warehouse)
                                    
                                    # 주문 상태를 "생산중"으로 변경 (입고 등록 시작 시)
                                    if selected_order.status == "승인":
                                        selected_order.status = "생산중"
                                    
                                    # 주문 상태 업데이트 (모든 항목 입고 완료 시)
                                    # 새로 추가된 항목도 포함하여 다시 조회
                                    db.flush()  # DB에 반영하여 조회 가능하도록
                                    
                                    total_received = {}
                                    all_receipts = db.query(Warehouse).filter(
                                        Warehouse.order_no == selected_order_no
                                    ).all()
                                    
                                    for receipt in all_receipts:
                                        key = (receipt.order_no, receipt.order_seq)
                                        total_received[key] = total_received.get(key, 0) + receipt.received_qty
                                    
                                    # 모든 주문 상세 항목이 입고 완료되었는지 확인
                                    all_received = True
                                    for detail in order_details:
                                        key = (detail.order_no, detail.order_seq)
                                        received_total = total_received.get(key, 0)
                                        if received_total < detail.order_qty:
                                            all_received = False
                                            break
                                    
                                    if all_received:
                                        selected_order.status = "입고완료"
                                        db.commit()
                                        st.success(f"✅ {len(receipt_items)}개 항목이 입고 등록되었습니다. 모든 항목 입고 완료로 주문 상태가 '입고완료'로 변경되었습니다.")
                                    else:
                                        db.commit()
                                        st.success(f"✅ {len(receipt_items)}개 항목이 입고 등록되었습니다.")
                                    
                                    st.rerun()
                                    
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ 입고 등록 중 오류 발생: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                else:
                    st.warning("주문 상세 정보가 없습니다.")
            
            # 입고 내역 조회
            st.markdown("---")
            st.markdown("### 입고 내역")
            
            receipts = db.query(Warehouse).filter(
                Warehouse.order_no == selected_order_no
            ).order_by(Warehouse.received_date.desc(), Warehouse.order_seq).all()
            
            if receipts:
                receipt_data = []
                for receipt in receipts:
                    receipt_data.append({
                        "입고일자": receipt.received_date.strftime("%Y-%m-%d"),
                        "순번": receipt.order_seq,
                        "품목명": receipt.item_name,
                        "입고수량": f"{receipt.received_qty:,}",
                        "입고자": receipt.received_by,
                        "등록일시": receipt.created_at.strftime("%Y-%m-%d %H:%M") if receipt.created_at else ""
                    })
                
                receipt_df = pd.DataFrame(receipt_data)
                st.dataframe(receipt_df, use_container_width=True, hide_index=True)
            else:
                st.info("입고 내역이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {str(e)}")
finally:
    close_db(db)


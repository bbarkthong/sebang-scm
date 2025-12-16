"""
출하 계획 페이지 (세방산업 주문담당자)
"""
import streamlit as st
from datetime import date, datetime
from auth.auth import require_role, get_current_user
from database.connection import get_db, close_db
from database.models import OrderMaster, OrderDetail, Warehouse, ShippingPlan
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

# 역할 확인 (주문담당자만 접근 가능)
require_role(["주문담당자"])

# 사이드바 표시
from utils.sidebar import show_sidebar
show_sidebar()

st.title("출하 계획")
st.markdown("---")

user = get_current_user()

# 탭 구성
tab1, tab2 = st.tabs(["재고 현황", "출하 계획 수립"])

db = get_db()
try:
    with tab1:
        st.subheader("입고 완료 재고 현황")
        
        # 입고 완료된 주문 조회
        completed_orders = db.query(OrderMaster).filter(
            OrderMaster.status == "입고완료"
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
        
        if not completed_orders:
            st.info("입고 완료된 주문이 없습니다.")
        else:
            # 재고 현황 집계
            inventory_data = []
            for order in completed_orders:
                order_details = db.query(OrderDetail).filter(
                    OrderDetail.order_no == order.order_no
                ).order_by(OrderDetail.order_seq).all()
                
                for detail in order_details:
                    # 입고 수량 집계
                    receipts = db.query(Warehouse).filter(
                        Warehouse.order_no == order.order_no,
                        Warehouse.order_seq == detail.order_seq
                    ).all()
                    total_received = sum(r.received_qty for r in receipts)
                    
                    # 출하 계획 수량 집계 (계획 + 지시 상태)
                    shipping_plans = db.query(ShippingPlan).filter(
                        ShippingPlan.order_no == order.order_no,
                        ShippingPlan.order_seq == detail.order_seq,
                        ShippingPlan.status.in_(["계획", "지시"])
                    ).all()
                    total_planned = sum(sp.planned_qty for sp in shipping_plans)
                    
                    # 출하 완료 수량
                    shipping_completed = db.query(ShippingPlan).filter(
                        ShippingPlan.order_no == order.order_no,
                        ShippingPlan.order_seq == detail.order_seq,
                        ShippingPlan.status == "출하완료"
                    ).all()
                    total_shipped = sum(sp.planned_qty for sp in shipping_completed)
                    
                    available_qty = total_received - total_planned - total_shipped
                    
                    inventory_data.append({
                        "주문번호": order.order_no,
                        "주문일자": order.order_date.strftime("%Y-%m-%d"),
                        "고객사": order.customer_company,
                        "순번": detail.order_seq,
                        "품목명": detail.item_name,
                        "주문수량": f"{detail.order_qty:,}",
                        "입고수량": f"{total_received:,}",
                        "출하계획": f"{total_planned:,}",
                        "출하완료": f"{total_shipped:,}",
                        "가용재고": f"{available_qty:,}" if available_qty > 0 else "0"
                    })
            
            if inventory_data:
                inventory_df = pd.DataFrame(inventory_data)
                st.dataframe(inventory_df, use_container_width=True, hide_index=True)
            else:
                st.info("재고 데이터가 없습니다.")
    
    with tab2:
        st.subheader("출하 계획 수립")
        st.markdown("""
        **출하 계획 등록 절차:**
        1. **주문 승인**: 주문담당자가 "주문 승인" 페이지에서 주문을 승인합니다. (상태: "대기" → "승인")
        2. **입고 등록**: 제조담당자가 "입고 등록" 페이지에서 생산 완료 후 입고 등록을 합니다. (상태: "승인" → "생산중" → "입고완료")
        3. **출하 계획 수립**: 입고완료 상태인 주문에 대해 출하수량과 출하예정일을 입력한 후 등록 버튼을 클릭합니다.
        """)
        
        # 입고 완료된 주문 목록
        completed_orders = db.query(OrderMaster).filter(
            OrderMaster.status == "입고완료"
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
        
        # 입고 완료되지 않은 주문도 표시 (참고용)
        waiting_orders = db.query(OrderMaster).filter(
            OrderMaster.status.in_(["대기", "승인", "생산중"])
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
        
        if not completed_orders:
            st.warning("⚠️ 출하 계획을 수립할 주문이 없습니다.")
            
            if waiting_orders:
                st.markdown("---")
                st.markdown("### 입고 대기 중인 주문 현황")
                st.info(f"💡 현재 {len(waiting_orders)}개의 주문이 입고 대기 중입니다. 아래 절차를 따라 입고 완료를 진행하세요.")
                
                # 상태별로 그룹화
                status_groups = {}
                for order in waiting_orders:
                    if order.status not in status_groups:
                        status_groups[order.status] = []
                    status_groups[order.status].append(order)
                
                for status, orders_in_status in status_groups.items():
                    status_name = {
                        "대기": "⏳ 승인 대기",
                        "승인": "✅ 승인 완료 (입고 등록 대기)",
                        "생산중": "🏭 생산 중 (입고 등록 진행 중)"
                    }.get(status, status)
                    
                    with st.expander(f"{status_name} ({len(orders_in_status)}건)"):
                        waiting_data = []
                        for order in orders_in_status:
                            # 입고 진행률 계산
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
                            
                            waiting_data.append({
                                "주문번호": order.order_no,
                                "주문일자": order.order_date.strftime("%Y-%m-%d"),
                                "고객사": order.customer_company,
                                "상태": order.status,
                                "우선순위": order.priority,
                                "입고진행률": f"{progress:.1f}% ({total_received:,}/{total_qty:,})"
                            })
                        waiting_df = pd.DataFrame(waiting_data)
                        st.dataframe(waiting_df, use_container_width=True, hide_index=True)
                        
                        # 다음 단계 안내
                        if status == "대기":
                            st.info("📋 **다음 단계**: 주문담당자가 '주문 승인' 페이지에서 이 주문을 승인해야 합니다.")
                        elif status == "승인":
                            st.info("📦 **다음 단계**: 제조담당자가 '입고 등록' 페이지에서 생산 완료 후 입고 등록을 해야 합니다.")
                        elif status == "생산중":
                            st.info("📦 **다음 단계**: 제조담당자가 '입고 등록' 페이지에서 남은 수량을 입고 등록하면 입고완료됩니다.")
        else:
            selected_order_no = st.selectbox(
                "주문 선택",
                options=[order.order_no for order in completed_orders],
                key="shipping_order_select"
            )
            
            if selected_order_no:
                selected_order = db.query(OrderMaster).filter(
                    OrderMaster.order_no == selected_order_no
                ).first()
                
                st.markdown(f"**선택된 주문:** {selected_order_no} ({selected_order.customer_company})")
                
                # 주문 상세 조회
                order_details = db.query(OrderDetail).filter(
                    OrderDetail.order_no == selected_order_no
                ).order_by(OrderDetail.order_seq).all()
                
                if order_details:
                    with st.form("shipping_plan_form"):
                        st.markdown("#### 출하 계획 입력")
                        
                        shipping_items = []
                        for detail in order_details:
                            # 입고 수량 집계
                            receipts = db.query(Warehouse).filter(
                                Warehouse.order_no == selected_order_no,
                                Warehouse.order_seq == detail.order_seq
                            ).all()
                            total_received = sum(r.received_qty for r in receipts)
                            
                            # 출하 계획 수량 집계 (계획 + 지시 상태)
                            shipping_plans = db.query(ShippingPlan).filter(
                                ShippingPlan.order_no == selected_order_no,
                                ShippingPlan.order_seq == detail.order_seq,
                                ShippingPlan.status.in_(["계획", "지시"])
                            ).all()
                            total_planned = sum(sp.planned_qty for sp in shipping_plans)
                            
                            # 출하 완료 수량
                            shipping_completed = db.query(ShippingPlan).filter(
                                ShippingPlan.order_no == selected_order_no,
                                ShippingPlan.order_seq == detail.order_seq,
                                ShippingPlan.status == "출하완료"
                            ).all()
                            total_shipped = sum(sp.planned_qty for sp in shipping_completed)
                            
                            available_qty = total_received - total_planned - total_shipped
                            
                            if available_qty > 0:
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.markdown(f"**{detail.item_name}**")
                                
                                with col2:
                                    st.markdown(f"가용재고: {available_qty:,}")
                                    st.caption(f"입고: {total_received:,} / 계획: {total_planned:,} / 완료: {total_shipped:,}")
                                
                                with col3:
                                    planned_qty = st.number_input(
                                        "출하수량",
                                        min_value=0,
                                        max_value=available_qty,
                                        value=min(available_qty, detail.order_qty - total_shipped),
                                        key=f"planned_qty_{detail.order_no}_{detail.order_seq}"
                                    )
                                
                                with col4:
                                    planned_date = st.date_input(
                                        "출하예정일",
                                        value=detail.planned_shipping_date or date.today(),
                                        key=f"planned_date_{detail.order_no}_{detail.order_seq}"
                                    )
                                
                                if planned_qty > 0:
                                    shipping_items.append({
                                        "order_no": detail.order_no,
                                        "order_seq": detail.order_seq,
                                        "planned_qty": planned_qty,
                                        "planned_date": planned_date
                                    })
                                
                                st.markdown("---")
                        
                        if not shipping_items:
                            st.warning("⚠️ 출하 계획을 수립할 항목이 없습니다.")
                            st.info("💡 가용재고가 있는 항목만 출하 계획을 수립할 수 있습니다. 입고 등록이 완료되었는지 확인해주세요.")
                        
                        submit_button = st.form_submit_button("📄 출하 계획 등록", use_container_width=True, type="primary")
                        
                        if submit_button:
                            if not shipping_items:
                                st.warning("출하 계획을 수립할 항목을 선택해주세요. (출하수량을 0보다 크게 입력해야 합니다)")
                            else:
                                # 검증
                                errors = []
                                for item in shipping_items:
                                    if item["planned_qty"] <= 0:
                                        errors.append(f"순번 {item['order_seq']}: 출하수량은 1 이상이어야 합니다.")
                                
                                if errors:
                                    st.error("\n".join(errors))
                                else:
                                    try:
                                        for item in shipping_items:
                                            shipping_plan = ShippingPlan(
                                                order_no=item["order_no"],
                                                order_seq=item["order_seq"],
                                                planned_shipping_date=item["planned_date"],
                                                planned_qty=item["planned_qty"],
                                                status="계획",
                                                created_by=user["username"]
                                            )
                                            db.add(shipping_plan)
                                        
                                        db.commit()
                                        st.success(f"✅ {len(shipping_items)}개 항목의 출하 계획이 성공적으로 등록되었습니다.")
                                        st.rerun()
                                        
                                    except Exception as e:
                                        db.rollback()
                                        st.error(f"❌ 출하 계획 등록 중 오류 발생: {str(e)}")
                                        import traceback
                                        st.code(traceback.format_exc())
                
                # 출하 계획 내역 및 출하 지시
                st.markdown("---")
                st.markdown("### 출하 계획 내역 및 출하 지시")
                
                shipping_plans = db.query(ShippingPlan).filter(
                    ShippingPlan.order_no == selected_order_no
                ).order_by(ShippingPlan.planned_shipping_date, ShippingPlan.order_seq).all()
                
                if shipping_plans:
                    # 상태별로 구분
                    planned_plans = [p for p in shipping_plans if p.status == "계획"]
                    instructed_plans = [p for p in shipping_plans if p.status == "지시"]
                    completed_plans = [p for p in shipping_plans if p.status == "출하완료"]
                    
                    plan_data = []
                    for plan in shipping_plans:
                        detail = db.query(OrderDetail).filter(
                            OrderDetail.order_no == plan.order_no,
                            OrderDetail.order_seq == plan.order_seq
                        ).first()
                        
                        plan_data.append({
                            "계획ID": plan.plan_id,
                            "순번": plan.order_seq,
                            "품목명": detail.item_name if detail else "",
                            "출하수량": f"{plan.planned_qty:,}",
                            "출하예정일": plan.planned_shipping_date.strftime("%Y-%m-%d"),
                            "상태": plan.status,
                            "등록일시": plan.created_at.strftime("%Y-%m-%d %H:%M") if plan.created_at else ""
                        })
                    
                    plan_df = pd.DataFrame(plan_data)
                    st.dataframe(plan_df, use_container_width=True, hide_index=True)
                    
                    # 상태별 요약
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("계획", f"{len(planned_plans)}건")
                    with col_stat2:
                        st.metric("지시", f"{len(instructed_plans)}건")
                    with col_stat3:
                        st.metric("완료", f"{len(completed_plans)}건")
                    
                    st.markdown("---")
                    
                    # 출하 지시 버튼 (계획 상태인 항목만)
                    if planned_plans:
                        st.markdown("#### 출하 지시")
                        st.info("💡 출하 계획을 검토한 후 출하 지시를 하면 발주사에게 출하 계획이 전달됩니다.")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("📤 출하 지시", use_container_width=True, type="primary", key="btn_shipping_instruct"):
                                try:
                                    for plan in planned_plans:
                                        plan.status = "지시"
                                    
                                    db.commit()
                                    st.success(f"✅ {len(planned_plans)}개 항목에 대한 출하 지시가 완료되었습니다.")
                                    st.rerun()
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ 출하 지시 중 오류 발생: {str(e)}")
                        
                        with col_btn2:
                            if st.button("📋 출하 지시서 출력", use_container_width=True, type="secondary", key="btn_print_instruct"):
                                st.info("출하 지시서 출력 기능은 준비 중입니다.")
                    
                    # 출하 완료 처리 (지시 상태인 항목만 - 발주사가 수신 확인 후)
                    if instructed_plans:
                        st.markdown("#### 출하 완료 처리")
                        st.info("💡 발주사가 수신 확인을 완료한 후 출하 완료 처리를 합니다.")
                        
                        if st.button("✅ 출하 완료 처리", use_container_width=True, type="primary", key="btn_shipping_complete"):
                            try:
                                for plan in instructed_plans:
                                    plan.status = "출하완료"
                                
                                # 주문 상세의 출하 수량 업데이트
                                for plan in instructed_plans:
                                    detail = db.query(OrderDetail).filter(
                                        OrderDetail.order_no == plan.order_no,
                                        OrderDetail.order_seq == plan.order_seq
                                    ).first()
                                    if detail:
                                        detail.shipping_qty = (detail.shipping_qty or 0) + plan.planned_qty
                                        if not detail.actual_shipping_date:
                                            detail.actual_shipping_date = plan.planned_shipping_date
                                        detail.shipping_amount = float(detail.shipping_qty * detail.unit_price)
                                
                                # 주문 상태 확인 (모든 항목 출하 완료 시)
                                all_shipped = True
                                order_details = db.query(OrderDetail).filter(
                                    OrderDetail.order_no == selected_order_no
                                ).all()
                                
                                for detail in order_details:
                                    total_shipped = sum(
                                        sp.planned_qty for sp in db.query(ShippingPlan).filter(
                                            ShippingPlan.order_no == detail.order_no,
                                            ShippingPlan.order_seq == detail.order_seq,
                                            ShippingPlan.status == "출하완료"
                                        ).all()
                                    )
                                    if total_shipped < detail.order_qty:
                                        all_shipped = False
                                        break
                                
                                if all_shipped:
                                    selected_order.status = "출하완료"
                                
                                db.commit()
                                st.success(f"✅ {len(instructed_plans)}개 항목의 출하 완료 처리가 완료되었습니다.")
                                st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ 출하 완료 처리 중 오류 발생: {str(e)}")
                    elif not planned_plans and not instructed_plans:
                        st.success("✅ 모든 출하 계획이 완료되었습니다.")
                else:
                    st.info("출하 계획 내역이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {str(e)}")
finally:
    close_db(db)


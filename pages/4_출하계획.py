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

# 역할 확인 (주문담당자만 접근 가능)
require_role(["주문담당자"])

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
                    
                    # 출하 계획 수량 집계
                    shipping_plans = db.query(ShippingPlan).filter(
                        ShippingPlan.order_no == order.order_no,
                        ShippingPlan.order_seq == detail.order_seq,
                        ShippingPlan.status == "계획"
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
                        "품목코드": detail.item_code,
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
        
        # 입고 완료된 주문 목록
        completed_orders = db.query(OrderMaster).filter(
            OrderMaster.status == "입고완료"
        ).order_by(OrderMaster.priority.desc(), OrderMaster.order_date).all()
        
        if not completed_orders:
            st.info("출하 계획을 수립할 주문이 없습니다.")
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
                            
                            # 출하 계획 수량 집계
                            shipping_plans = db.query(ShippingPlan).filter(
                                ShippingPlan.order_no == selected_order_no,
                                ShippingPlan.order_seq == detail.order_seq,
                                ShippingPlan.status == "계획"
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
                                    st.caption(f"코드: {detail.item_code}")
                                
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
                            st.info("출하 계획을 수립할 항목이 없습니다.")
                        
                        submit_button = st.form_submit_button("출하 계획 등록", use_container_width=True, type="primary")
                        
                        if submit_button:
                            if not shipping_items:
                                st.warning("출하 계획을 수립할 항목을 선택해주세요.")
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
                                    st.success(f"{len(shipping_items)}개 항목의 출하 계획이 등록되었습니다.")
                                    st.rerun()
                                    
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"출하 계획 등록 중 오류 발생: {str(e)}")
                
                # 출하 계획 내역
                st.markdown("---")
                st.markdown("### 출하 계획 내역")
                
                shipping_plans = db.query(ShippingPlan).filter(
                    ShippingPlan.order_no == selected_order_no
                ).order_by(ShippingPlan.planned_shipping_date, ShippingPlan.order_seq).all()
                
                if shipping_plans:
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
                    
                    # 출하 완료 처리
                    if st.button("선택된 계획 출하 완료 처리", type="primary"):
                        pending_plans = [p for p in shipping_plans if p.status == "계획"]
                        if pending_plans:
                            for plan in pending_plans:
                                plan.status = "출하완료"
                            
                            # 주문 상세의 출하 수량 업데이트
                            for plan in pending_plans:
                                detail = db.query(OrderDetail).filter(
                                    OrderDetail.order_no == plan.order_no,
                                    OrderDetail.order_seq == plan.order_seq
                                ).first()
                                if detail:
                                    detail.shipping_qty = (detail.shipping_qty or 0) + plan.planned_qty
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
                            st.success("출하 완료 처리되었습니다.")
                            st.rerun()
                        else:
                            st.info("출하 완료 처리할 계획이 없습니다.")
                else:
                    st.info("출하 계획 내역이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {str(e)}")
finally:
    close_db(db)


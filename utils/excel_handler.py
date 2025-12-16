"""
엑셀 업로드/다운로드 처리
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from utils.validators import (
    validate_item_name, validate_qty, validate_unit_price
)
from decimal import Decimal
from database.connection import get_db, close_db
from database.models import ItemMaster

# streamlit은 선택적 import (테스트 환경에서는 필요 없음)
try:
    import streamlit as st
except ImportError:
    st = None


def create_order_template():
    """주문 엑셀 템플릿 생성"""
    # 품목 마스터에서 활성 품목 조회
    db = get_db()
    try:
        items = db.query(ItemMaster).filter(ItemMaster.is_active == "Y").order_by(ItemMaster.item_name).limit(5).all()
        if items:
            item_names = [item.item_name for item in items]
            unit_prices = [float(item.unit_price) for item in items]
        else:
            item_names = ["분리막 A형", "분리막 B형"]
            unit_prices = [1000.00, 1500.00]
    finally:
        close_db(db)
    
    template_data = {
        "품목명": item_names,
        "주문수량": [100] * len(item_names),
        "단가(참고용)": unit_prices,  # 참고용으로만 표시, 실제로는 품목 마스터의 단가 사용
        "납품예정일": [""] * len(item_names)  # 선택사항
    }
    
    df = pd.DataFrame(template_data)
    return df


def save_template_file(file_path: str):
    """템플릿 파일 저장"""
    df = create_order_template()
    df.to_excel(file_path, index=False, engine='openpyxl')
    return file_path


def parse_excel_file(uploaded_file) -> tuple[bool, list, str]:
    """
    엑셀 파일 파싱
    Returns: (성공여부, 주문상세리스트, 에러메시지)
    """
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # 필수 컬럼 확인 (품목코드와 단가는 제외 - 품목 마스터에서 관리)
        required_columns = ["품목명", "주문수량"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, [], f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
        
        # 품목 마스터 조회 (품목명으로 품목코드와 단가 찾기)
        db = get_db()
        try:
            items = db.query(ItemMaster).filter(ItemMaster.is_active == "Y").all()
            item_dict = {item.item_name: {"item_code": item.item_code, "unit_price": float(item.unit_price)} for item in items}
        finally:
            close_db(db)
        
        # 데이터 검증 및 변환
        order_details = []
        errors = []
        
        for idx, row in df.iterrows():
            row_num = idx + 2  # 엑셀 행 번호 (헤더 제외)
            
            # 품목명 검증 및 품목코드 찾기
            item_name = str(row["품목명"]).strip() if pd.notna(row["품목명"]) else ""
            is_valid, error_msg = validate_item_name(item_name)
            if not is_valid:
                errors.append(f"행 {row_num}: {error_msg}")
                continue
            
            # 품목 마스터에서 품목코드와 단가 찾기
            if item_name not in item_dict:
                errors.append(f"행 {row_num}: 등록되지 않은 품목명입니다: {item_name}")
                continue
            
            item_code = item_dict[item_name]["item_code"]
            unit_price = item_dict[item_name]["unit_price"]  # 품목 마스터의 단가 사용
            
            # 주문수량 검증
            try:
                order_qty = int(row["주문수량"])
                is_valid, error_msg = validate_qty(order_qty)
                if not is_valid:
                    errors.append(f"행 {row_num}: {error_msg}")
                    continue
            except (ValueError, TypeError):
                errors.append(f"행 {row_num}: 주문수량은 숫자여야 합니다.")
                continue
            
            # 엑셀에 단가 컬럼이 있으면 경고만 표시 (품목 마스터의 단가를 사용)
            if "단가" in df.columns and pd.notna(row["단가"]):
                excel_unit_price = None
                try:
                    excel_unit_price = float(row["단가"])
                except (ValueError, TypeError):
                    pass
                
                if excel_unit_price is not None and abs(excel_unit_price - unit_price) > 0.01:
                    errors.append(f"행 {row_num}: 엑셀의 단가({excel_unit_price:,.0f})는 무시되고 품목 마스터의 단가({unit_price:,.0f})가 사용됩니다.")
            
            # 납품예정일 처리 (선택사항)
            planned_shipping_date = None
            # "출하예정일" 또는 "납품예정일" 컬럼 모두 지원 (하위 호환성)
            date_column = None
            if "납품예정일" in df.columns:
                date_column = "납품예정일"
            elif "출하예정일" in df.columns:
                date_column = "출하예정일"
            
            if date_column and pd.notna(row[date_column]):
                try:
                    if isinstance(row[date_column], str):
                        planned_shipping_date = pd.to_datetime(row[date_column]).date()
                    else:
                        planned_shipping_date = row[date_column].date() if hasattr(row[date_column], 'date') else None
                except:
                    errors.append(f"행 {row_num}: 납품예정일 형식이 올바르지 않습니다.")
            
            order_detail = {
                "item_code": item_code,
                "item_name": item_name,
                "order_qty": order_qty,
                "unit_price": float(unit_price),
                "planned_shipping_date": planned_shipping_date
            }
            
            order_details.append(order_detail)
        
        if errors:
            error_message = "\n".join(errors)
            if order_details:
                error_message = f"일부 데이터에 오류가 있습니다:\n{error_message}"
            return len(order_details) > 0, order_details, error_message
        
        if len(order_details) == 0:
            return False, [], "주문 상세 데이터가 없습니다."
        
        return True, order_details, ""
        
    except Exception as e:
        return False, [], f"엑셀 파일 처리 중 오류 발생: {str(e)}"


def download_template():
    """템플릿 파일 다운로드용 바이트 반환"""
    df = create_order_template()
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='주문상세')
    output.seek(0)
    return output.getvalue()



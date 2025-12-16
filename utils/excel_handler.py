"""
엑셀 업로드/다운로드 처리
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
from utils.validators import (
    validate_item_code, validate_item_name, validate_qty, validate_unit_price
)
from decimal import Decimal


def create_order_template():
    """주문 엑셀 템플릿 생성"""
    template_data = {
        "품목코드": ["ITEM001", "ITEM002"],
        "품목명": ["분리막 A형", "분리막 B형"],
        "주문수량": [100, 200],
        "단가": [1000.00, 1500.00],
        "출하예정일": ["2024-12-31", "2024-12-31"]
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
        
        # 필수 컬럼 확인
        required_columns = ["품목코드", "품목명", "주문수량", "단가"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, [], f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
        
        # 데이터 검증 및 변환
        order_details = []
        errors = []
        
        for idx, row in df.iterrows():
            row_num = idx + 2  # 엑셀 행 번호 (헤더 제외)
            
            # 품목코드 검증
            item_code = str(row["품목코드"]).strip() if pd.notna(row["품목코드"]) else ""
            is_valid, error_msg = validate_item_code(item_code)
            if not is_valid:
                errors.append(f"행 {row_num}: {error_msg}")
                continue
            
            # 품목명 검증
            item_name = str(row["품목명"]).strip() if pd.notna(row["품목명"]) else ""
            is_valid, error_msg = validate_item_name(item_name)
            if not is_valid:
                errors.append(f"행 {row_num}: {error_msg}")
                continue
            
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
            
            # 단가 검증
            try:
                unit_price = Decimal(str(row["단가"]))
                is_valid, error_msg = validate_unit_price(unit_price)
                if not is_valid:
                    errors.append(f"행 {row_num}: {error_msg}")
                    continue
            except (ValueError, TypeError):
                errors.append(f"행 {row_num}: 단가는 숫자여야 합니다.")
                continue
            
            # 출하예정일 처리 (선택사항)
            planned_shipping_date = None
            if "출하예정일" in df.columns and pd.notna(row["출하예정일"]):
                try:
                    if isinstance(row["출하예정일"], str):
                        planned_shipping_date = pd.to_datetime(row["출하예정일"]).date()
                    else:
                        planned_shipping_date = row["출하예정일"].date() if hasattr(row["출하예정일"], 'date') else None
                except:
                    errors.append(f"행 {row_num}: 출하예정일 형식이 올바르지 않습니다.")
            
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


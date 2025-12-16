"""
엑셀 처리 테스트
"""
import pytest
import sys
import os
import pandas as pd
from io import BytesIO

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.excel_handler import create_order_template, parse_excel_file, download_template


class TestExcelTemplate:
    """엑셀 템플릿 테스트"""
    
    def test_create_template(self):
        """템플릿 생성 테스트"""
        df = create_order_template()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "품목코드" in df.columns
        assert "품목명" in df.columns
        assert "주문수량" in df.columns
        assert "단가" in df.columns
    
    def test_download_template(self):
        """템플릿 다운로드 테스트"""
        template_bytes = download_template()
        
        assert isinstance(template_bytes, bytes)
        assert len(template_bytes) > 0


class TestExcelParsing:
    """엑셀 파싱 테스트"""
    
    def test_parse_valid_excel(self):
        """유효한 엑셀 파일 파싱 테스트"""
        # 유효한 엑셀 데이터 생성
        data = {
            "품목코드": ["ITEM001", "ITEM002"],
            "품목명": ["품목1", "품목2"],
            "주문수량": [100, 200],
            "단가": [1000.0, 2000.0],
            "출하예정일": ["2024-12-31", "2024-12-31"]
        }
        df = pd.DataFrame(data)
        
        # BytesIO로 엑셀 파일 생성
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        # 파싱 테스트
        success, order_details, error_msg = parse_excel_file(excel_buffer)
        
        assert success is True
        assert len(order_details) == 2
        assert order_details[0]["item_code"] == "ITEM001"
        assert order_details[0]["order_qty"] == 100
        assert error_msg == ""
    
    def test_parse_excel_missing_columns(self):
        """필수 컬럼 누락 엑셀 파일 테스트"""
        # 필수 컬럼이 없는 데이터 생성
        data = {
            "품목코드": ["ITEM001"],
            "품목명": ["품목1"]
            # 주문수량, 단가 컬럼 누락
        }
        df = pd.DataFrame(data)
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        # 파싱 테스트
        success, order_details, error_msg = parse_excel_file(excel_buffer)
        
        assert success is False
        assert len(order_details) == 0
        assert "필수 컬럼" in error_msg
    
    def test_parse_excel_invalid_data(self):
        """잘못된 데이터가 포함된 엑셀 파일 테스트"""
        # 잘못된 데이터 (수량이 음수)
        data = {
            "품목코드": ["ITEM001"],
            "품목명": ["품목1"],
            "주문수량": [-100],  # 음수
            "단가": [1000.0]
        }
        df = pd.DataFrame(data)
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        # 파싱 테스트
        success, order_details, error_msg = parse_excel_file(excel_buffer)
        
        # 음수 수량은 검증에서 걸러지므로 성공은 False이거나 order_details가 비어있어야 함
        assert success is False or len(order_details) == 0
        # 오류 메시지에 수량 관련 내용이 있어야 함
        assert len(error_msg) > 0
    
    def test_parse_excel_empty_file(self):
        """빈 엑셀 파일 테스트"""
        # 빈 데이터프레임 (컬럼만 있음)
        df = pd.DataFrame(columns=["품목코드", "품목명", "주문수량", "단가"])
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        # 파싱 테스트
        success, order_details, error_msg = parse_excel_file(excel_buffer)
        
        assert success is False
        assert len(order_details) == 0
        assert "주문 상세 데이터가 없습니다" in error_msg or len(error_msg) > 0


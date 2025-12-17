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
        # 품목코드는 더 이상 템플릿에 포함되지 않음 (품목 마스터에서 관리)
        assert "품목명" in df.columns
        assert "주문수량" in df.columns
        assert "단가(참고용)" in df.columns or "단가" in df.columns
        assert "납품예정일" in df.columns
    
    def test_download_template(self):
        """템플릿 다운로드 테스트"""
        template_bytes = download_template()
        
        assert isinstance(template_bytes, bytes)
        assert len(template_bytes) > 0


class TestExcelParsing:
    """엑셀 파싱 테스트"""
    
    def test_parse_valid_excel(self):
        """유효한 엑셀 파일 파싱 테스트"""
        # 먼저 테스트용 품목 마스터 데이터가 필요함
        # 실제 품목 마스터에 있는 품목명을 사용해야 함
        from database.connection import get_db, close_db
        from database.models import ItemMaster
        
        db = get_db()
        try:
            # 활성 품목 조회
            items = db.query(ItemMaster).filter(ItemMaster.is_active == "Y").limit(2).all()
            if not items:
                pytest.skip("품목 마스터에 활성 품목이 없습니다.")
            
            # 유효한 엑셀 데이터 생성 (품목 마스터의 실제 품목명 사용)
            data = {
                "품목명": [items[0].item_name, items[1].item_name if len(items) > 1 else items[0].item_name],
                "주문수량": [100, 200],
                "납품예정일": ["2024-12-31", "2024-12-31"]
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
            assert order_details[0]["item_code"] == items[0].item_code
            assert order_details[0]["order_qty"] == 100
            assert error_msg == "" or len(error_msg) == 0
        finally:
            close_db(db)
    
    def test_parse_excel_missing_columns(self):
        """필수 컬럼 누락 엑셀 파일 테스트"""
        # 필수 컬럼이 없는 데이터 생성 (품목코드는 더 이상 필수 아님)
        data = {
            "품목명": ["품목1"]
            # 주문수량 컬럼 누락
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
        # 먼저 테스트용 품목 마스터 데이터가 필요함
        from database.connection import get_db, close_db
        from database.models import ItemMaster
        
        db = get_db()
        try:
            items = db.query(ItemMaster).filter(ItemMaster.is_active == "Y").limit(1).all()
            if not items:
                pytest.skip("품목 마스터에 활성 품목이 없습니다.")
            
            # 잘못된 데이터 (수량이 음수)
            data = {
                "품목명": [items[0].item_name],
                "주문수량": [-100]  # 음수
            }
            df = pd.DataFrame(data)
        finally:
            close_db(db)
        
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
        # 빈 데이터프레임 (컬럼만 있음, 품목코드는 더 이상 필요 없음)
        df = pd.DataFrame(columns=["품목명", "주문수량"])
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_buffer.seek(0)
        
        # 파싱 테스트
        success, order_details, error_msg = parse_excel_file(excel_buffer)
        
        assert success is False
        assert len(order_details) == 0
        assert "주문 상세 데이터가 없습니다" in error_msg or len(error_msg) > 0


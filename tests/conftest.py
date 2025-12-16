"""
pytest 설정 및 공통 fixture
"""
import pytest
import os
import tempfile
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base


@pytest.fixture(scope="function")
def test_db():
    """테스트용 데이터베이스 세션 생성"""
    # 임시 데이터베이스 파일 생성
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # 테스트용 엔진 생성
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    
    # 세션 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def sample_user_data():
    """샘플 사용자 데이터"""
    return {
        "user_id": "test_user_001",
        "username": "test_user",
        "password": "test123",
        "role": "발주사",
        "company_name": "테스트회사"
    }


@pytest.fixture
def sample_order_data():
    """샘플 주문 데이터"""
    return {
        "order_no": "ORD-TEST-001",
        "order_date": "2024-01-15",
        "order_type": "일반",
        "customer_company": "테스트회사",
        "created_by": "test_user"
    }


@pytest.fixture
def sample_order_detail_data():
    """샘플 주문 상세 데이터"""
    return {
        "order_no": "ORD-TEST-001",
        "order_seq": 1,
        "item_code": "ITEM001",
        "item_name": "테스트 품목",
        "order_qty": 100,
        "unit_price": 1000.00
    }


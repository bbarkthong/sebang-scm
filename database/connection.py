"""
데이터베이스 연결 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import DB_PATH, DB_DIR
import os

# 데이터 디렉토리 생성
os.makedirs(DB_DIR, exist_ok=True)

# SQLite 엔진 생성
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # 세션은 명시적으로 닫아야 함


def close_db(db: Session):
    """데이터베이스 세션 닫기"""
    db.close()


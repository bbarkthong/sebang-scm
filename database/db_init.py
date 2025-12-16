"""
데이터베이스 초기화 스크립트
"""
from database.connection import engine
from database.models import Base, User, ItemMaster
from config import DB_PATH
import bcrypt
import os
from datetime import datetime


def init_db():
    """데이터베이스 초기화 및 기본 사용자 생성"""
    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    from database.connection import SessionLocal
    db = SessionLocal()

    try:
        # 기본 사용자 확인
        existing_users = db.query(User).count()
        if existing_users == 0:
            # 기본 사용자 생성
            default_users = [
                {
                    "user_id": "user001",
                    "username": "samsung_sdi",
                    "password": "samsung123",
                    "role": "발주사",
                    "company_name": "삼성SDI"
                },
                {
                    "user_id": "user002",
                    "username": "hyundai_motor",
                    "password": "hyundai123",
                    "role": "발주사",
                    "company_name": "현대자동차"
                },
                {
                    "user_id": "user003",
                    "username": "order_manager",
                    "password": "order123",
                    "role": "주문담당자",
                    "company_name": "세방산업"
                },
                {
                    "user_id": "user004",
                    "username": "manufacturing",
                    "password": "mfg123",
                    "role": "제조담당자",
                    "company_name": "세방산업"
                }
            ]

            for user_data in default_users:
                password_hash = bcrypt.hashpw(
                    user_data["password"].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')

                user = User(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    password_hash=password_hash,
                    role=user_data["role"],
                    company_name=user_data["company_name"]
                )
                db.add(user)

            db.commit()
            print("기본 사용자 생성 완료.")
        else:
            print("기본 사용자가 이미 존재합니다.")
        
        # 품목 마스터 확인 및 생성
        existing_items = db.query(ItemMaster).count()
        if existing_items == 0:
            # 기본 품목 생성
            default_items = [
                {
                    "item_code": "ITEM001",
                    "item_name": "분리막 A형",
                    "lead_time_days": 30,  # 주문일자 기준 30일 후 납품 가능
                    "unit_price": 1000.00,
                    "is_active": "Y"
                },
                {
                    "item_code": "ITEM002",
                    "item_name": "분리막 B형",
                    "lead_time_days": 30,
                    "unit_price": 1500.00,
                    "is_active": "Y"
                },
                {
                    "item_code": "ITEM003",
                    "item_name": "분리막 C형",
                    "lead_time_days": 45,
                    "unit_price": 2000.00,
                    "is_active": "Y"
                },
                {
                    "item_code": "ITEM004",
                    "item_name": "분리막 D형",
                    "lead_time_days": 60,
                    "unit_price": 2500.00,
                    "is_active": "Y"
                },
                {
                    "item_code": "ITEM005",
                    "item_name": "분리막 E형",
                    "lead_time_days": 20,
                    "unit_price": 1200.00,
                    "is_active": "Y"
                }
            ]
            
            for item_data in default_items:
                item = ItemMaster(
                    item_code=item_data["item_code"],
                    item_name=item_data["item_name"],
                    lead_time_days=item_data["lead_time_days"],
                    unit_price=item_data["unit_price"],
                    is_active=item_data["is_active"]
                )
                db.add(item)
            
            db.commit()
            print("품목 마스터 생성 완료.")
        else:
            print("품목 마스터가 이미 존재합니다.")
        
        print("데이터베이스 초기화 완료.")
    except Exception as e:
        db.rollback()
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()


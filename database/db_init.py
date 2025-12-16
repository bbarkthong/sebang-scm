"""
데이터베이스 초기화 스크립트
"""
from database.connection import engine
from database.models import Base, User
from config import DB_PATH
import bcrypt
import os


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
            print("데이터베이스 초기화 완료. 기본 사용자가 생성되었습니다.")
        else:
            print("데이터베이스가 이미 초기화되어 있습니다.")
    except Exception as e:
        db.rollback()
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()


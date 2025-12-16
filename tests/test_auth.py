"""
인증 시스템 테스트
"""
import pytest
import bcrypt
from datetime import datetime
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import User
from auth.auth import hash_password, verify_password


class TestPasswordHashing:
    """비밀번호 해싱 테스트"""
    
    def test_hash_password(self):
        """비밀번호 해싱 테스트"""
        password = "test123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)
    
    def test_verify_password_correct(self):
        """올바른 비밀번호 검증 테스트"""
        password = "test123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """잘못된 비밀번호 검증 테스트"""
        password = "test123"
        wrong_password = "wrong123"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestLogin:
    """로그인 기능 테스트"""
    
    def test_login_success(self, test_db, sample_user_data):
        """로그인 성공 테스트"""
        # 사용자 생성
        password_hash = hash_password(sample_user_data["password"])
        user = User(
            user_id=sample_user_data["user_id"],
            username=sample_user_data["username"],
            password_hash=password_hash,
            role=sample_user_data["role"],
            company_name=sample_user_data["company_name"]
        )
        test_db.add(user)
        test_db.commit()
        
        # 비밀번호 검증 테스트 (login 함수는 streamlit 의존성이 있어 직접 테스트)
        assert verify_password(sample_user_data["password"], password_hash) is True
        
        # 사용자 조회 테스트
        found_user = test_db.query(User).filter(
            User.username == sample_user_data["username"]
        ).first()
        
        assert found_user is not None
        assert found_user.username == sample_user_data["username"]
        assert found_user.role == sample_user_data["role"]
    
    def test_login_wrong_username(self, test_db, sample_user_data):
        """잘못된 사용자명으로 로그인 테스트"""
        # 사용자 생성
        password_hash = hash_password(sample_user_data["password"])
        user = User(
            user_id=sample_user_data["user_id"],
            username=sample_user_data["username"],
            password_hash=password_hash,
            role=sample_user_data["role"],
            company_name=sample_user_data["company_name"]
        )
        test_db.add(user)
        test_db.commit()
        
        # 잘못된 사용자명 조회
        found_user = test_db.query(User).filter(
            User.username == "wrong_user"
        ).first()
        
        assert found_user is None
    
    def test_login_wrong_password(self, test_db, sample_user_data):
        """잘못된 비밀번호로 로그인 테스트"""
        # 사용자 생성
        password_hash = hash_password(sample_user_data["password"])
        user = User(
            user_id=sample_user_data["user_id"],
            username=sample_user_data["username"],
            password_hash=password_hash,
            role=sample_user_data["role"],
            company_name=sample_user_data["company_name"]
        )
        test_db.add(user)
        test_db.commit()
        
        # 잘못된 비밀번호 검증
        assert verify_password("wrong_password", password_hash) is False


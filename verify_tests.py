#!/usr/bin/env python3.12
"""테스트 검증 스크립트"""
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("테스트 환경 검증")
print("=" * 70)

# 1. 필수 모듈 확인
print("\n[1] 필수 모듈 확인")
try:
    import pytest
    print(f"  ✓ pytest {pytest.__version__}")
except ImportError:
    print("  ✗ pytest가 설치되지 않았습니다.")
    print("    설치: pip install pytest")
    sys.exit(1)

try:
    import pandas
    print(f"  ✓ pandas {pandas.__version__}")
except ImportError:
    print("  ✗ pandas가 설치되지 않았습니다.")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"  ✓ sqlalchemy {sqlalchemy.__version__}")
except ImportError:
    print("  ✗ sqlalchemy가 설치되지 않았습니다.")
    sys.exit(1)

try:
    import bcrypt
    print(f"  ✓ bcrypt")
except ImportError:
    print("  ✗ bcrypt가 설치되지 않았습니다.")
    sys.exit(1)

# 2. 프로젝트 모듈 확인
print("\n[2] 프로젝트 모듈 확인")
modules = [
    'config',
    'database.models',
    'database.connection',
    'utils.validators',
    'utils.excel_handler',
    'auth.auth',
]

for mod_name in modules:
    try:
        __import__(mod_name)
        print(f"  ✓ {mod_name}")
    except Exception as e:
        print(f"  ✗ {mod_name}: {e}")
        sys.exit(1)

# 3. 간단한 함수 테스트
print("\n[3] 함수 실행 테스트")
try:
    from utils.validators import validate_order_no
    is_valid, msg = validate_order_no("TEST-001")
    assert is_valid is True
    print(f"  ✓ validate_order_no: {is_valid}, {msg}")
except Exception as e:
    print(f"  ✗ validate_order_no 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from auth.auth import hash_password, verify_password
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    print(f"  ✓ password hashing/verification")
except Exception as e:
    print(f"  ✗ password 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("모든 검증 통과! pytest를 실행할 수 있습니다.")
print("=" * 70)
print("\n실행 명령:")
print("  python3.12 -m pytest tests/ -v")
print()


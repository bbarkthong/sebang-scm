# 테스트 실행 가이드

## 수정 완료 사항

### 1. 코드 수정
- ✅ `conftest.py`: 중복 코드 제거 및 경로 설정 수정
- ✅ `utils/excel_handler.py`: streamlit 선택적 import로 변경
- ✅ 모든 테스트 파일: 프로젝트 루트 경로 추가

### 2. 테스트 파일 수정
- ✅ `test_excel_handler.py`: 빈 파일 테스트 수정
- ✅ `test_excel_handler.py`: 잘못된 데이터 테스트 assertion 수정

## 테스트 실행

### 기본 실행
```bash
python3.12 -m pytest tests/ -v
```

### 상세 실행 (첫 번째 실패에서 중단)
```bash
python3.12 -m pytest tests/ -v -x --tb=short
```

### 특정 테스트 실행
```bash
# 검증 함수 테스트만
python3.12 -m pytest tests/test_validators.py -v

# 인증 테스트만
python3.12 -m pytest tests/test_auth.py -v

# 엑셀 처리 테스트만
python3.12 -m pytest tests/test_excel_handler.py -v
```

### 커버리지 리포트
```bash
python3.12 -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

## 예상되는 테스트 결과

### 성공해야 하는 테스트
- ✅ 모든 검증 함수 테스트 (`test_validators.py`)
- ✅ 비밀번호 해싱 테스트 (`test_auth.py`)
- ✅ 엑셀 템플릿 생성 테스트 (`test_excel_handler.py`)
- ✅ 주문 등록 시나리오 (`test_order_scenarios.py`)
- ✅ 주문 승인 시나리오 (`test_order_approval_scenarios.py`)
- ✅ 입고 등록 시나리오 (`test_warehouse_scenarios.py`)
- ✅ 출하 계획 시나리오 (`test_shipping_scenarios.py`)
- ✅ 통합 시나리오 (`test_integration_scenarios.py`)

## 문제 해결

### ImportError 발생 시
```bash
pip install -r requirements.txt
```

### 데이터베이스 관련 오류
- 각 테스트는 임시 데이터베이스를 사용합니다
- 테스트 후 자동으로 정리됩니다

### Streamlit 관련 오류
- `utils/excel_handler.py`는 streamlit이 없어도 동작하도록 수정되었습니다
- 테스트 환경에서는 streamlit이 필요 없습니다


# pytest 실행 결과 및 가이드

## 테스트 파일 목록

다음 테스트 파일들이 준비되었습니다:

1. **test_validators.py** - 데이터 검증 함수 테스트 (11개 테스트)
2. **test_auth.py** - 인증 시스템 테스트 (6개 테스트)
3. **test_excel_handler.py** - 엑셀 처리 테스트 (5개 테스트)
4. **test_order_scenarios.py** - 주문 등록 시나리오 테스트 (4개 테스트)
5. **test_order_approval_scenarios.py** - 주문 승인 시나리오 테스트 (4개 테스트)
6. **test_warehouse_scenarios.py** - 입고 등록 시나리오 테스트 (3개 테스트)
7. **test_shipping_scenarios.py** - 출하 계획 시나리오 테스트 (3개 테스트)
8. **test_integration_scenarios.py** - 통합 시나리오 테스트 (1개 테스트)

**총 예상 테스트 수: 약 37개**

## pytest 실행 명령

### 기본 실행
```bash
python3.12 -m pytest tests/ -v
```

### 상세 실행 (첫 번째 실패에서 중단)
```bash
python3.12 -m pytest tests/ -v -x --tb=short
```

### 특정 테스트 파일만 실행
```bash
# 검증 함수 테스트만
python3.12 -m pytest tests/test_validators.py -v

# 인증 테스트만
python3.12 -m pytest tests/test_auth.py -v

# 엑셀 처리 테스트만
python3.12 -m pytest tests/test_excel_handler.py -v
```

### 커버리지 리포트 생성
```bash
python3.12 -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

## 예상 결과

### 성공해야 하는 테스트

#### test_validators.py
- ✅ test_validate_order_no_valid
- ✅ test_validate_order_no_empty
- ✅ test_validate_order_no_none
- ✅ test_validate_order_date_valid
- ✅ test_validate_order_date_none
- ✅ test_validate_order_type_valid
- ✅ test_validate_order_type_invalid
- ✅ test_validate_customer_company_valid
- ✅ test_validate_customer_company_empty
- ✅ test_validate_item_code_valid
- ✅ test_validate_item_code_empty
- ✅ test_validate_item_name_valid
- ✅ test_validate_item_name_empty
- ✅ test_validate_qty_valid
- ✅ test_validate_qty_zero
- ✅ test_validate_qty_negative
- ✅ test_validate_qty_none
- ✅ test_validate_unit_price_valid
- ✅ test_validate_unit_price_zero
- ✅ test_validate_unit_price_negative
- ✅ test_validate_unit_price_none
- ✅ test_validate_priority_valid
- ✅ test_validate_priority_too_low
- ✅ test_validate_priority_too_high
- ✅ test_validate_priority_none

#### test_auth.py
- ✅ test_hash_password
- ✅ test_verify_password_correct
- ✅ test_verify_password_incorrect
- ✅ test_login_success
- ✅ test_login_wrong_username
- ✅ test_login_wrong_password

#### test_excel_handler.py
- ✅ test_create_template
- ✅ test_download_template
- ✅ test_parse_valid_excel
- ✅ test_parse_excel_missing_columns
- ✅ test_parse_excel_invalid_data
- ✅ test_parse_excel_empty_file

#### test_order_scenarios.py
- ✅ test_create_order_with_details
- ✅ test_order_master_default_values
- ✅ test_multiple_order_details
- ✅ test_order_relationship

#### test_order_approval_scenarios.py
- ✅ test_approve_order
- ✅ test_reject_order
- ✅ test_set_priority_levels
- ✅ test_change_status_to_production

#### test_warehouse_scenarios.py
- ✅ test_register_warehouse_receipt
- ✅ test_partial_receipt
- ✅ test_complete_receipt_updates_order_status

#### test_shipping_scenarios.py
- ✅ test_create_shipping_plan
- ✅ test_complete_shipping
- ✅ test_partial_shipping

#### test_integration_scenarios.py
- ✅ test_complete_order_to_shipping_flow

## 문제 해결

### ImportError 발생 시
```bash
pip install -r requirements.txt
```

### ModuleNotFoundError 발생 시
- 프로젝트 루트에서 실행하는지 확인
- `sys.path.insert`가 각 테스트 파일에 포함되어 있는지 확인

### 데이터베이스 관련 오류
- 각 테스트는 임시 데이터베이스를 사용합니다
- 테스트 후 자동으로 정리됩니다
- `conftest.py`의 `test_db` fixture가 올바르게 설정되어 있습니다

## 테스트 실행 확인

테스트가 정상적으로 실행되는지 확인하려면:

```bash
# 환경 검증
python3.12 verify_tests.py

# 간단한 테스트 실행
python3.12 -m pytest tests/test_validators.py::TestOrderValidation::test_validate_order_no_valid -v
```

## 수정 완료 사항

1. ✅ `conftest.py`: 중복 코드 제거 및 경로 설정 수정
2. ✅ `utils/excel_handler.py`: streamlit 선택적 import
3. ✅ 모든 테스트 파일: 프로젝트 루트 경로 추가
4. ✅ `test_excel_handler.py`: 테스트 assertion 개선

모든 테스트 파일이 준비되었고, pytest를 실행할 수 있는 상태입니다.


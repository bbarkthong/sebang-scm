# 테스트 가이드

## 테스트 실행 방법

### 모든 테스트 실행
```bash
python3.12 -m pytest tests/ -v
```

### 특정 테스트 파일 실행
```bash
python3.12 -m pytest tests/test_validators.py -v
```

### 특정 테스트 클래스 실행
```bash
python3.12 -m pytest tests/test_validators.py::TestOrderValidation -v
```

### 특정 테스트 함수 실행
```bash
python3.12 -m pytest tests/test_validators.py::TestOrderValidation::test_validate_order_no_valid -v
```

### 커버리지 리포트 생성
```bash
python3.12 -m pytest tests/ --cov=. --cov-report=html
```

## 테스트 구조

### 1. 단위 테스트 (Unit Tests)

#### `test_validators.py`
- 데이터 검증 유틸리티 테스트
- 주문번호, 주문일자, 품목코드 등 검증 함수 테스트

#### `test_auth.py`
- 인증 시스템 테스트
- 비밀번호 해싱 및 검증 테스트
- 사용자 조회 테스트

#### `test_excel_handler.py`
- 엑셀 처리 테스트
- 템플릿 생성 및 다운로드 테스트
- 엑셀 파일 파싱 테스트

### 2. 시나리오 테스트 (Scenario Tests)

#### `test_order_scenarios.py`
- 주문 등록 시나리오 테스트
- 주문 마스터 및 상세 생성 테스트
- 여러 주문 상세 항목 테스트
- 주문 관계 테스트

#### `test_order_approval_scenarios.py`
- 주문 승인 시나리오 테스트
- 주문 승인/거부 테스트
- 우선순위 설정 테스트
- 상태 변경 테스트

#### `test_warehouse_scenarios.py`
- 입고 등록 시나리오 테스트
- 입고 등록 테스트
- 부분 입고 테스트
- 전체 입고 완료 시 상태 변경 테스트

#### `test_shipping_scenarios.py`
- 출하 계획 시나리오 테스트
- 출하 계획 생성 테스트
- 출하 완료 처리 테스트
- 부분 출하 테스트

### 3. 통합 테스트 (Integration Tests)

#### `test_integration_scenarios.py`
- 전체 프로세스 통합 테스트
- 주문 등록부터 출하까지 전체 플로우 테스트

## 테스트 Fixture

### `test_db`
- 각 테스트마다 임시 데이터베이스 생성
- 테스트 후 자동으로 정리

### `sample_user_data`
- 샘플 사용자 데이터 제공

### `sample_order_data`
- 샘플 주문 마스터 데이터 제공

### `sample_order_detail_data`
- 샘플 주문 상세 데이터 제공

## 테스트 작성 가이드

1. 각 테스트는 독립적으로 실행 가능해야 합니다.
2. 테스트 데이터는 fixture를 사용하여 생성합니다.
3. 테스트 후 데이터베이스는 자동으로 정리됩니다.
4. 테스트 함수명은 `test_`로 시작해야 합니다.
5. 테스트 클래스명은 `Test`로 시작해야 합니다.

## 주의사항

- Streamlit 의존성이 있는 함수는 직접 테스트하기 어려울 수 있습니다.
- 데이터베이스 테스트는 임시 파일을 사용하므로 실제 데이터에 영향을 주지 않습니다.
- 각 테스트는 격리되어 실행되므로 순서에 의존하지 않아야 합니다.


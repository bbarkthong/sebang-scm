# 테스트 가이드

## 테스트 실행 방법

프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.

### 모든 테스트 실행
```bash
python -m pytest tests/ -v
```

### 특정 테스트 파일 실행
```bash
python -m pytest tests/test_validators.py -v
```

### 커버리지 리포트 생성
```bash
python -m pytest tests/ --cov=services --cov=utils --cov-report=html
```
*Note: 커버리지 측정 대상을 `services`와 `utils`로 지정하여 비즈니스 로직과 유틸리티 함수에 대한 테스트 커버리지를 확인합니다.*

## 테스트 구조

### 1. 단위 테스트 (Unit Tests)

#### `test_validators.py`
- 데이터 검증 유틸리티 함수들의 순수성을 테스트합니다.

#### `test_auth.py`
- 인증 시스템의 핵심 기능(비밀번호 해싱 및 검증)을 테스트합니다.

#### `test_excel_handler.py`
- 엑셀 템플릿 생성 및 파일 파싱 로직을 테스트합니다.

### 2. 서비스 계층 테스트 (Service Layer Tests)

이 테스트들은 각 비즈니스 로직이 담긴 서비스 함수들이 정확히 동작하는지 검증합니다. 데이터베이스 상태 변경을 포함하는 시나리오를 다룹니다.

#### `test_order_scenarios.py`
- `order_service`의 주문 생성 로직을 테스트합니다.

#### `test_order_approval_scenarios.py`
- `approval_service`의 주문 승인, 거부, 상태 변경 로직을 테스트합니다.

#### `test_warehouse_scenarios.py`
- `warehousing_service`의 입고 등록 및 재고 계산 로직을 테스트합니다.

#### `test_shipping_scenarios.py`
- `shipping_service` 및 `shipping_registration_service`의 출하 계획 생성, 지시, 완료 로직을 테스트합니다.

### 3. 통합 테스트 (Integration Tests)

#### `test_integration_scenarios.py`
- **주문 등록 → 승인 → 입고 → 출하 계획 → 출하 완료** 까지 이어지는 전체 프로세스를 서비스 계층의 함수들을 통해 순차적으로 테스트하여 전체 시스템의 정합성을 검증합니다.

## 테스트 Fixture

- **`test_db`**: 각 테스트 함수마다 독립적인 인메모리(SQLite) 데이터베이스 세션을 제공하고, 테스트 종료 후 자동으로 정리합니다.
- **`sample_*_data`**: 테스트에 필요한 샘플 데이터를 제공합니다.

## 테스트 작성 가이드

1.  각 테스트는 독립적으로 실행 가능해야 합니다.
2.  서비스 계층 테스트는 UI와 분리된 비즈니스 로직을 검증하는 데 집중합니다.
3.  Streamlit 페이지 파일(`pages/*.py`)은 직접 테스트하지 않습니다. 대신 그 페이지들이 호출하는 서비스 함수를 테스트합니다.
4.  테스트 함수명은 `test_`로 시작하고, 테스트 클래스명은 `Test`로 시작합니다.
# E2E 테스트 가이드

## 개요
Playwright를 사용한 End-to-End 테스트입니다.

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

## 테스트 실행

### 방법 1: 실행 스크립트 사용 (권장)
```bash
python run_e2e_tests.py
```

### 방법 2: pytest 직접 실행
```bash
# Streamlit 서버가 실행 중이어야 합니다
streamlit run app.py --server.port 8501

# 다른 터미널에서 테스트 실행
pytest tests/e2e -v -m e2e --browser chromium
```

## 테스트 시나리오

### 시나리오 1: 발주사 주문 등록
- 삼성SDI 계정으로 로그인
- 수동 주문 등록
- 발주서 생성
- 엑셀 업로드 주문 등록
- 발주서 생성
- 대시보드 확인 및 로그아웃

### 시나리오 2: 주문담당자 승인/거부
- 발주관리자 계정으로 로그인
- 대시보드 확인
- 수동 발주 내역 거부
- 엑셀 업로드 내역 수량 조정 후 승인
- 대시보드 확인 및 로그아웃

### 시나리오 3: 제조담당자 입고 등록
- 생산관리자 계정으로 로그인
- 승인된 건 입고 등록
- 대시보드 확인 및 로그아웃

### 시나리오 4: 주문담당자 출하 지시
- 발주관리자 계정으로 로그인
- 대시보드 확인
- 출하 지시 등록

## 테스트 계정

- **발주사 (삼성SDI)**: `samsung_sdi` / `samsung123`
- **발주사 (현대자동차)**: `hyundai_motor` / `hyundai123`
- **주문담당자**: `order_manager` / `order123`
- **제조담당자**: `manufacturing` / `mfg123`

## 주의사항

1. 테스트 실행 전 Streamlit 서버가 실행 중이어야 합니다.
2. 테스트는 실제 데이터베이스를 사용하므로, 테스트 전 데이터베이스 백업을 권장합니다.
3. 테스트는 순차적으로 실행되며, 각 시나리오는 이전 시나리오의 데이터에 의존할 수 있습니다.


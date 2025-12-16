# 세방리튬배터리 SCM 시스템

세방리튬배터리의 공급망 관리(Supply Chain Management) 시스템입니다. 발주부터 출하까지의 전 과정을 통합 관리합니다.

## 주요 기능

### 1. 주문 등록 (발주사)
- 수동 주문 등록
- 엑셀 파일 업로드를 통한 일괄 주문 등록
- 주문 템플릿 다운로드

### 2. 주문 승인 (주문담당자)
- 주문 승인/거부 처리
- 우선순위 설정 (1~9 레벨)
- 주문 상태 관리

### 3. 입고 등록 (제조담당자)
- 생산 완료 내역 창고 입고 등록
- 입고 수량 및 날짜 관리
- 입고 내역 조회

### 4. 출하 계획 (주문담당자)
- 재고 현황 확인
- 출하 계획 수립
- 출하 완료 처리

### 5. 대시보드
- 역할별 주요 지표 및 현황 확인
- 최근 활동 내역

## 기술 스택

- **프레임워크**: Streamlit
- **데이터베이스**: SQLite + SQLAlchemy ORM
- **엑셀 처리**: pandas, openpyxl
- **인증**: 세션 기반 (Streamlit session_state)
- **비밀번호 해싱**: bcrypt

## 설치 및 실행

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화

데이터베이스는 애플리케이션 최초 실행 시 자동으로 초기화됩니다.

수동 초기화가 필요한 경우:

```bash
python database/db_init.py
```

### 3. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## 기본 사용자 계정

시스템 초기화 시 다음 기본 사용자가 생성됩니다:

### 발주사 계정
- **삼성SDI**: `samsung_sdi` / `samsung123`
- **현대자동차**: `hyundai_motor` / `hyundai123`

### 세방리튬배터리 계정
- **주문담당자**: `order_manager` / `order123`
- **제조담당자**: `manufacturing` / `mfg123`

## 프로젝트 구조

```
sebang-scm/
├── app.py                 # Streamlit 메인 애플리케이션
├── config.py              # 설정 파일
├── database/
│   ├── models.py          # SQLAlchemy 모델 정의
│   ├── db_init.py         # 데이터베이스 초기화 스크립트
│   └── connection.py      # DB 연결 관리
├── auth/
│   └── auth.py            # 인증 로직
├── pages/
│   ├── 1_주문등록.py      # 주문 등록 페이지
│   ├── 2_주문승인.py      # 주문 승인 페이지
│   ├── 3_입고등록.py      # 입고 등록 페이지
│   ├── 4_출하계획.py      # 출하 계획 페이지
│   └── 5_대시보드.py      # 대시보드 페이지
├── utils/
│   ├── excel_handler.py   # 엑셀 처리
│   └── validators.py      # 데이터 검증
├── .streamlit/
│   ├── config.toml        # Streamlit 설정
│   └── style.css          # 커스텀 스타일
└── requirements.txt       # Python 패키지 의존성
```

## 데이터베이스 스키마

### 주요 테이블
- **users**: 사용자 정보
- **order_master**: 주문 마스터
- **order_detail**: 주문 상세
- **warehouse**: 창고 입고 내역
- **shipping_plan**: 출하 계획

## 사용 방법

1. 로그인 페이지에서 역할에 맞는 계정으로 로그인합니다.
2. 사이드바의 페이지 메뉴를 통해 각 기능에 접근합니다.
3. 발주사는 주문 등록 페이지에서 주문을 등록합니다.
4. 주문담당자는 주문 승인 페이지에서 주문을 승인하고 우선순위를 설정합니다.
5. 제조담당자는 입고 등록 페이지에서 생산 완료 내역을 등록합니다.
6. 주문담당자는 출하 계획 페이지에서 재고를 확인하고 출하 계획을 수립합니다.

## 주의사항

- 데이터베이스 파일(`data/sebang_scm.db`)은 프로젝트 루트의 `data` 디렉토리에 생성됩니다.
- 프로덕션 환경에서는 SQLite 대신 PostgreSQL 또는 MySQL 사용을 권장합니다.
- 비밀번호는 bcrypt로 해싱되어 저장됩니다.

## 라이선스

이 프로젝트는 세방리튬배터리 내부 사용을 위한 것입니다.


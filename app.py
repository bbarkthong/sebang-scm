"""
세방리튬배터리 SCM 시스템 메인 애플리케이션
"""
import streamlit as st
from auth.auth import is_authenticated, show_login_page, logout, get_current_user
from database.db_init import init_db

# 페이지 설정
st.set_page_config(
    page_title="세방리튬배터리 SCM 시스템",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 적용
def load_custom_css():
    import os
    css_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'style.css')
    try:
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        # CSS 파일이 없어도 계속 진행
        pass
    
    # Streamlit 기본 페이지 네비게이션 강제 숨김 (인라인 CSS로 추가 보장)
    st.markdown("""
    <style>
    /* Streamlit 기본 페이지 네비게이션 완전히 숨김 - 모든 가능한 선택자 사용 */
    div[data-testid="stSidebarNav"],
    nav[data-testid="stSidebarNav"],
    section[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNav"],
    .css-1d391kg,
    .css-1lcbmhc,
    .css-1y4p8pa {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# 데이터베이스 초기화 (최초 실행 시)
if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"데이터베이스 초기화 실패: {str(e)}")

# 인증 확인
if not is_authenticated():
    show_login_page()
    st.stop()
else:
    # 사용자 정보 확인 (세션 만료 체크)
    user = get_current_user()
    if not user or not user.get('username'):
        # 세션이 만료된 경우 로그인 페이지로 이동
        logout()
        show_login_page()
        st.stop()
    
    # 사이드바
    with st.sidebar:
        st.title("세방리튬배터리 SCM")
        st.markdown("---")
        
        st.markdown(f"**사용자:** {user.get('username', '')}")
        st.markdown(f"**역할:** {user.get('role', '')}")
        if user.get('company_name'):
            st.markdown(f"**회사:** {user.get('company_name', '')}")
        
        st.markdown("---")
        
        if st.button("로그아웃", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 메뉴")
        
        # 역할별 메뉴 표시
        role = user.get('role', '')
        
        # 대시보드 (모든 역할 접근 가능)
        if st.button("📊 대시보드", use_container_width=True, key="btn_dashboard"):
            st.switch_page("pages/5_대시보드.py")
        
        # 발주사 메뉴
        if role == "발주사":
            if st.button("📝 주문 등록", use_container_width=True, key="btn_order_reg"):
                st.switch_page("pages/1_주문등록.py")
        
        # 주문담당자 메뉴
        elif role == "주문담당자":
            if st.button("✅ 주문 승인", use_container_width=True, key="btn_order_approval"):
                st.switch_page("pages/2_주문승인.py")
            if st.button("🚚 출하 계획", use_container_width=True, key="btn_shipping"):
                st.switch_page("pages/4_출하계획.py")
        
        # 제조담당자 메뉴
        elif role == "제조담당자":
            if st.button("📦 입고 등록", use_container_width=True, key="btn_warehouse"):
                st.switch_page("pages/3_입고등록.py")
        
        # Streamlit 기본 페이지 네비게이션 숨김
        st.markdown("""
        <style>
        /* Streamlit 기본 페이지 네비게이션 완전히 숨김 */
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # 메인 콘텐츠
    st.title("세방리튬배터리 SCM 시스템")
    st.markdown("---")
    
    user = get_current_user()
    st.info(f"환영합니다, {user.get('username', '')}님! ({user.get('role', '')})")
    
    st.markdown("""
    ### 시스템 개요
    
    세방리튬배터리 SCM 시스템은 발주부터 출하까지의 전 과정을 관리하는 통합 시스템입니다.
    
    #### 주요 기능
    
    1. **주문 등록** (발주사)
       - 수동 주문 등록
       - 엑셀 파일 업로드를 통한 일괄 주문 등록
    
    2. **주문 승인** (주문담당자)
       - 주문 승인/거부
       - 우선순위 설정 (1~9)
       - 주문 상태 관리
    
    3. **입고 등록** (제조담당자)
       - 생산 완료 내역 창고 입고 등록
       - 입고 수량 및 날짜 관리
    
    4. **출하 계획** (주문담당자)
       - 재고 현황 확인
       - 출하 계획 수립
       - 출하 완료 처리
    
    5. **대시보드**
       - 역할별 주요 지표 및 현황 확인
    
    #### 사용 방법
    
    왼쪽 사이드바의 페이지 메뉴를 통해 각 기능에 접근할 수 있습니다.
    """)
    
    # 역할별 안내
    role = user.get('role', '')
    if role == "발주사":
        st.markdown("""
        #### 발주사 안내
        - **주문 등록** 페이지에서 새로운 주문을 등록할 수 있습니다.
        - 엑셀 템플릿을 다운로드하여 일괄 주문 등록이 가능합니다.
        - **대시보드**에서 내 주문 현황을 확인할 수 있습니다.
        """)
    elif role == "주문담당자":
        st.markdown("""
        #### 주문담당자 안내
        - **주문 승인** 페이지에서 대기 중인 주문을 승인하고 우선순위를 설정할 수 있습니다.
        - **출하 계획** 페이지에서 재고 현황을 확인하고 출하 계획을 수립할 수 있습니다.
        - **대시보드**에서 전체 주문 현황 및 긴급 주문을 확인할 수 있습니다.
        """)
    elif role == "제조담당자":
        st.markdown("""
        #### 제조담당자 안내
        - **입고 등록** 페이지에서 생산 완료된 제품을 창고에 입고 등록할 수 있습니다.
        - **대시보드**에서 생산 대기 주문 및 최근 입고 내역을 확인할 수 있습니다.
        """)


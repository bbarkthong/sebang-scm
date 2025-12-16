"""
사이드바 공통 함수
"""
import streamlit as st
from auth.auth import get_current_user, logout


def show_sidebar():
    """공통 사이드바 표시"""
    with st.sidebar:
        st.title("세방산업 SCM")
        st.markdown("---")
        
        user = get_current_user()
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
        div[data-testid="stSidebarNav"],
        nav[data-testid="stSidebarNav"],
        section[data-testid="stSidebarNav"],
        ul[data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        </style>
        """, unsafe_allow_html=True)


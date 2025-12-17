import streamlit as st
import os
from auth.auth import is_authenticated, show_login_page, logout
from database.db_init import init_db
from utils.sidebar import show_sidebar
from pages import (
    page_1_order_registration,
    page_2_order_approval,
    page_3_warehousing,
    page_4_shipping_plan,
    page_5_dashboard,
    page_6_shipping_registration
)

# --- Page Configuration ---
st.set_page_config(
    page_title="세방산업 SCM 시스템",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # 메뉴 숨김
)

# --- Custom CSS ---
def load_custom_css():
    """세방산업 디자인 시스템 CSS 로드"""
    # 외부 CSS 파일 로드
    try:
        css_path = os.path.join(os.path.dirname(__file__), ".streamlit", "style.css")
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        # CSS 파일 로드 실패 시 인라인 스타일 사용
        st.markdown("""
        <style>
        /* Hide Streamlit's default hamburger menu and page navigation */
        div[data-testid="stSidebarNav"],
        nav[data-testid="stSidebarNav"],
        section[data-testid="stSidebarNav"],
        ul[data-testid="stSidebarNav"],
        li[data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # 로그인 페이지일 때 사이드바 자동 접기
    if not is_authenticated():
        st.markdown("""
        <script>
        // 로그인 페이지일 때 사이드바 자동 접기
        window.addEventListener('load', function() {
            // 사이드바 접기 버튼 찾기
            const sidebarButton = document.querySelector('[data-testid="collapsedControl"]');
            if (sidebarButton) {
                // 사이드바가 열려있으면 접기
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar && sidebar.offsetWidth > 0) {
                    sidebarButton.click();
                }
            }
        });
        
        // 사이드바 상태 확인 및 접기
        setTimeout(function() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const sidebarButton = document.querySelector('[data-testid="collapsedControl"]');
            if (sidebar && sidebarButton && sidebar.offsetWidth > 0) {
                sidebarButton.click();
            }
        }, 100);
        </script>
        <style>
        /* 로그인 페이지일 때 사이드바 숨기기 */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

# --- Page Definitions ---
PAGES = {
    "대시보드": page_5_dashboard,
    "주문등록": page_1_order_registration,
    "주문승인": page_2_order_approval,
    "입고등록": page_3_warehousing,
    "출하계획": page_4_shipping_plan,
    "출하등록": page_6_shipping_registration,
}

# --- Main Application Logic ---
def main():
    """Main function to run the Streamlit app."""
    load_custom_css()

    # Initialize database if not already done
    if "db_initialized" not in st.session_state:
        try:
            init_db()
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"데이터베이스 초기화 실패: {e}")
            st.stop()

    # --- Authentication Check ---
    if not is_authenticated():
        show_login_page()
        st.stop()

    # --- Sidebar and Page Navigation ---
    # The show_sidebar function will now control the st.session_state.current_page
    show_sidebar(PAGES)

    # --- Render the Current Page ---
    # Default to Dashboard if no page is set
    current_page_name = st.session_state.get("current_page", "대시보드")
    page_function = PAGES.get(current_page_name)

    if page_function:
        page_function()
    else:
        st.error("페이지를 찾을 수 없습니다.")
        st.session_state.current_page = "대시보드"
        st.rerun()

if __name__ == "__main__":
    main()
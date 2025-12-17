import streamlit as st
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
    page_title="세방리튬배터리 SCM",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
def load_custom_css():
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
    /* Additional selectors to ensure it's hidden */
    .css-1d391kg, .css-1lcbmhc, .css-1y4p8pa {
        display: none !important;
    }
    /* Hide Streamlit's sidebar navigation completely */
    [data-testid="stSidebarNav"] {
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
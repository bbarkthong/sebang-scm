import streamlit as st
from auth.auth import get_current_user, logout

# --- Role-to-Page Mapping ---
# Defines which pages are visible to each role.
ROLE_PAGES = {
    "발주사": ["대시보드", "주문등록", "출하등록"],
    "주문담당자": ["대시보드", "주문승인", "출하계획"],
    "제조담당자": ["대시보드", "입고등록"],
}

# --- Icon Mapping ---
# Maps page names to icons for a better UI.
PAGE_ICONS = {
    "대시보드": "📊",
    "주문등록": "📝",
    "주문승인": "✅",
    "입고등록": "📦",
    "출하계획": "🚚",
    "출하등록": "📦",
}

def show_sidebar(pages: dict):
    """
    Renders the sidebar navigation and user information.

    Args:
        pages (dict): A dictionary mapping page names to their functions.
                      This is used to filter pages based on user role.
    """
    # Streamlit 기본 페이지 네비게이션 숨김
    st.markdown("""
    <style>
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
    
    with st.sidebar:
        st.title("세방리튬배터리 SCM")
        st.markdown("---")

        # --- Menu ---
        st.markdown("### 메뉴")

        user = get_current_user()
        role = user.get("role", "")
        
        # Get the list of pages accessible by the current user's role
        accessible_pages = ROLE_PAGES.get(role, ["대시보드"])

        # Display buttons for accessible pages
        for page_name in accessible_pages:
            if page_name in pages: # Ensure the page is defined in the app
                icon = PAGE_ICONS.get(page_name, "")
                if st.button(f"{icon} {page_name}", use_container_width=True, key=f"sidebar_{page_name}"):
                    st.session_state.current_page = page_name
                    st.rerun()

        st.markdown("---")

        # --- User Information ---
        st.markdown("#### 사용자 정보")
        st.caption(f"**{user.get('username', '')}** ({user.get('role', '')})")
        if user.get('company_name'):
            st.caption(f"*{user.get('company_name', '')}*")

        st.markdown("---")

        if st.button("로그아웃", use_container_width=True, type="secondary"):
            logout()
            # After logout, is_authenticated() will be false, and the login page will show.
            st.rerun()
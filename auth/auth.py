"""
인증 로직 (로그인/로그아웃/세션 관리)
"""
import streamlit as st
import bcrypt
from database.connection import get_db, close_db
from database.models import User


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def login(username: str, password: str) -> tuple[bool, str, dict]:
    """
    로그인 처리
    Returns: (성공여부, 메시지, 사용자정보)
    """
    db = get_db()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return False, "사용자명이 존재하지 않습니다.", {}
        
        if not verify_password(password, user.password_hash):
            return False, "비밀번호가 일치하지 않습니다.", {}
        
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "company_name": user.company_name
        }
        
        return True, "로그인 성공", user_info
    except Exception as e:
        return False, f"로그인 중 오류 발생: {str(e)}", {}
    finally:
        close_db(db)


def logout():
    """로그아웃 처리"""
    if "user" in st.session_state:
        del st.session_state["user"]
    if "authenticated" in st.session_state:
        st.session_state["authenticated"] = False


def is_authenticated() -> bool:
    """인증 상태 확인"""
    authenticated = st.session_state.get("authenticated", False)
    user = st.session_state.get("user", {})
    
    # 세션이 있지만 사용자 정보가 없으면 인증되지 않은 것으로 처리
    if authenticated and (not user or not user.get("username")):
        return False
    
    return authenticated


def get_current_user() -> dict:
    """현재 로그인한 사용자 정보 반환"""
    return st.session_state.get("user", {})


def require_auth():
    """인증이 필요한 페이지에서 사용"""
    if not is_authenticated():
        logout()  # 세션 정리
        show_login_page()
        st.stop()


def require_role(allowed_roles: list):
    """특정 역할만 접근 가능하도록 제한"""
    require_auth()
    user = get_current_user()
    
    # 사용자 정보가 없으면 로그인 페이지로 이동
    if not user or not user.get("username"):
        logout()
        show_login_page()
        st.stop()
    
    if user.get("role") not in allowed_roles:
        st.error(f"이 페이지는 {', '.join(allowed_roles)}만 접근할 수 있습니다.")
        st.info("접근 권한이 없습니다. 메인 페이지로 돌아가주세요.")
        if st.button("메인 페이지로 이동"):
            st.switch_page("app.py")
        st.stop()


def show_login_page():
    """로그인 페이지 표시"""
    st.title("세방리튬배터리 SCM 시스템")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("사용자명", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        submit_button = st.form_submit_button("로그인", use_container_width=True)
        
        if submit_button:
            if not username or not password:
                st.error("사용자명과 비밀번호를 입력해주세요.")
            else:
                success, message, user_info = login(username, password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user_info
                    st.success(message)
                    # 로그인 성공 후 대시보드로 이동
                    st.switch_page("pages/page_5_dashboard.py")
                else:
                    st.error(message)
    
    # 기본 사용자 정보 안내
    with st.expander("테스트 계정 정보"):
        st.markdown("""
        **발주사 계정:**
        - 삼성SDI: `samsung_sdi` / `samsung123`
        - 현대자동차: `hyundai_motor` / `hyundai123`
        
        **세방리튬배터리 계정:**
        - 주문담당자: `order_manager` / `order123`
        - 제조담당자: `manufacturing` / `mfg123`
        """)


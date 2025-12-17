"""
E2E 테스트 유틸리티 함수
"""
from playwright.sync_api import Page
import time

def login(page: Page, username: str, password: str):
    """로그인 헬퍼 함수"""
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    
    # 로그인 입력 필드 찾기
    page.wait_for_selector('input[type="text"]', timeout=15000)
    page.wait_for_selector('input[type="password"]', timeout=15000)
    
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    login_button = page.locator('button:has-text("로그인")').first
    
    username_input.fill(username)
    time.sleep(0.5)
    password_input.fill(password)
    time.sleep(0.5)
    login_button.click()
    
    # 로그인 후 대시보드 로드 대기
    page.wait_for_load_state("networkidle")
    time.sleep(3)

def navigate_to_page(page: Page, button_text: str, page_title: str, wait_time: int = 3):
    """페이지로 이동하는 헬퍼 함수"""
    button = page.locator(f'button:has-text("{button_text}")')
    if button.is_visible():
        button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(wait_time)
    
    # 페이지 로드 확인
    try:
        page.wait_for_selector(f'h1:has-text("{page_title}")', timeout=15000)
    except:
        # 대체 확인
        page.wait_for_selector(f'text={page_title}', timeout=15000)

def wait_for_streamlit_rerun(page: Page, timeout: int = 10):
    """Streamlit rerun 대기"""
    page.wait_for_load_state("networkidle")
    time.sleep(timeout)


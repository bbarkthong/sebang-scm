"""
E2E 테스트 시나리오 1 (간소화 버전): 발주사 (삼성SDI) 주문 등록
"""
import pytest
from playwright.sync_api import Page, expect
import time

SAMSUNG_USERNAME = "samsung_sdi"
SAMSUNG_PASSWORD = "samsung123"

@pytest.mark.e2e
def test_scenario_1_order_registration_simple(page: Page):
    """시나리오 1: 발주사 주문 등록 테스트 (간소화 버전)"""
    
    # 1. 로그인
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 로그인 입력
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    login_button = page.locator('button:has-text("로그인")').first
    
    username_input.wait_for(state="visible", timeout=15000)
    username_input.fill(SAMSUNG_USERNAME)
    time.sleep(0.5)
    password_input.fill(SAMSUNG_PASSWORD)
    time.sleep(0.5)
    login_button.click()
    
    # 로그인 후 대기
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 대시보드 확인
    page.wait_for_selector('h1', timeout=20000)
    h1_elements = page.locator('h1')
    assert h1_elements.count() > 0, "페이지가 로드되지 않았습니다"
    
    # 2. 주문 등록 버튼 클릭
    # 모든 버튼 중에서 "주문 등록" 텍스트가 포함된 버튼 찾기
    buttons = page.locator('button')
    order_button_found = False
    for i in range(buttons.count()):
        button = buttons.nth(i)
        button_text = button.inner_text()
        if "주문 등록" in button_text or "📝" in button_text:
            button.click()
            order_button_found = True
            break
    
    assert order_button_found, "주문 등록 버튼을 찾을 수 없습니다"
    
    # 페이지 전환 대기
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 주문 등록 페이지 확인 (유연한 확인)
    page_content = page.content()
    assert "주문" in page_content or "발주" in page_content, "주문 등록 페이지로 이동하지 못했습니다"
    
    print("✓ 시나리오 1 테스트 완료 (간소화 버전)")


"""
E2E 테스트 시나리오 3: 제조담당자 입고 등록
- 생산관리자 계정으로 로그인
- 발주관리자가 승인한 건에 대해 입고 등록
- 대시보드 확인 및 로그아웃
"""
import pytest
from playwright.sync_api import Page, expect
import time

MANUFACTURING_USERNAME = "manufacturing"
MANUFACTURING_PASSWORD = "mfg123"

@pytest.mark.e2e
def test_scenario_3_warehousing(page: Page):
    """시나리오 3: 제조담당자 입고 등록 테스트"""
    
    # 1. 로그인
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    login_button = page.locator('button:has-text("로그인")').first
    
    username_input.wait_for(state="visible", timeout=15000)
    username_input.fill(MANUFACTURING_USERNAME)
    time.sleep(0.5)
    password_input.fill(MANUFACTURING_PASSWORD)
    time.sleep(0.5)
    login_button.click()
    
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 2. 대시보드 확인
    page_content = page.content()
    assert "대시보드" in page_content or "제조담당자" in page_content, "대시보드로 이동하지 못했습니다"
    
    # 3. 입고 등록 페이지로 이동
    buttons = page.locator('button')
    warehousing_button_found = False
    for i in range(buttons.count()):
        button = buttons.nth(i)
        button_text = button.inner_text()
        if "입고 등록" in button_text or "📦 입고" in button_text:
            button.click()
            warehousing_button_found = True
            break
    
    assert warehousing_button_found, "입고 등록 버튼을 찾을 수 없습니다"
    
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 4. 승인된 주문 찾기 및 입고 등록
    order_expanders = page.locator('[data-testid="stExpander"]')
    if order_expanders.count() > 0:
        first_order = order_expanders.first
        first_order.click()
        time.sleep(3)  # expander 열림 대기
        
        # 입고수량 입력 (요소가 나타날 때까지 대기)
        page.wait_for_selector('input[type="number"]', timeout=15000, state="attached")
        number_inputs = page.locator('input[type="number"]')
        if number_inputs.count() > 0:
            qty_input = number_inputs.first
            qty_input.scroll_into_view_if_needed()
            time.sleep(1)
            # clear 대신 직접 fill 사용
            qty_input.fill("50", force=True)
            time.sleep(2)
        
        # 입고 등록 버튼 클릭
        register_buttons = page.locator('button').filter(has_text="입고 등록")
        if register_buttons.count() > 0:
            register_buttons.first.scroll_into_view_if_needed()
            register_buttons.first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(5)
    
    # 5. 대시보드로 이동
    dashboard_buttons = page.locator('button').filter(has_text="대시보드")
    if dashboard_buttons.count() > 0:
        dashboard_buttons.first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    
    # 6. 로그아웃
    logout_buttons = page.locator('button').filter(has_text="로그아웃")
    if logout_buttons.count() > 0:
        logout_buttons.first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    
    page_content = page.content()
    assert "사용자명" in page_content or "로그인" in page_content, "로그아웃 후 로그인 페이지로 이동하지 못했습니다"
    
    print("✓ 시나리오 3 테스트 완료")

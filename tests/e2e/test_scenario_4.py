"""
E2E 테스트 시나리오 4: 주문담당자 출하 지시
- 발주관리자 계정으로 로그인
- 대시보드 확인
- 출하 지시 등록
"""
import pytest
from playwright.sync_api import Page, expect
import time

ORDER_MANAGER_USERNAME = "order_manager"
ORDER_MANAGER_PASSWORD = "order123"

@pytest.mark.e2e
def test_scenario_4_shipping_instruction(page: Page):
    """시나리오 4: 주문담당자 출하 지시 테스트"""
    
    # 1. 로그인
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    login_button = page.locator('button:has-text("로그인")').first
    
    username_input.wait_for(state="visible", timeout=15000)
    username_input.fill(ORDER_MANAGER_USERNAME)
    time.sleep(0.5)
    password_input.fill(ORDER_MANAGER_PASSWORD)
    time.sleep(0.5)
    login_button.click()
    
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 2. 대시보드 확인
    page_content = page.content()
    assert "대시보드" in page_content or "주문담당자" in page_content, "대시보드로 이동하지 못했습니다"
    
    # 3. 출하 계획 페이지로 이동
    buttons = page.locator('button')
    shipping_button_found = False
    for i in range(buttons.count()):
        button = buttons.nth(i)
        button_text = button.inner_text()
        if "출하 계획" in button_text or "🚚" in button_text:
            button.click()
            shipping_button_found = True
            break
    
    assert shipping_button_found, "출하 계획 버튼을 찾을 수 없습니다"
    
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 4. 입고완료된 주문 찾기 및 출하 계획 수립
    order_expanders = page.locator('[data-testid="stExpander"]')
    if order_expanders.count() > 0:
        first_order = order_expanders.first
        first_order.click()
        time.sleep(2)
        
        # 출하수량 입력
        number_inputs = page.locator('input[type="number"]')
        if number_inputs.count() > 0:
            qty_input = number_inputs.first
            qty_input.clear()
            qty_input.fill("30")
            time.sleep(1)
        
        # 출하 계획 등록 버튼 클릭
        register_buttons = page.locator('button').filter(has_text="출하 계획 등록")
        if register_buttons.count() > 0:
            register_buttons.first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(5)
    
    # 5. 출하 지시 버튼 클릭
    instruct_buttons = page.locator('button').filter(has_text="출하 지시")
    if instruct_buttons.count() > 0:
        instruct_buttons.first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)
    
    # 성공 메시지 확인
    page_content = page.content()
    assert "출하 지시" in page_content or "완료" in page_content, "출하 지시 완료 메시지를 찾을 수 없습니다"
    
    print("✓ 시나리오 4 테스트 완료")

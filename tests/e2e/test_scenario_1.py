"""
E2E 테스트 시나리오 1: 발주사 (삼성SDI) 주문 등록
- 삼성 계정으로 로그인
- 수동 발주 등록
- 발주서 생성
- 엑셀 업로드를 통해 발주 등록
- 발주서 생성
- 대시보드 확인 및 로그아웃
"""
import pytest
from playwright.sync_api import Page, expect
import time

SAMSUNG_USERNAME = "samsung_sdi"
SAMSUNG_PASSWORD = "samsung123"

@pytest.mark.e2e
def test_scenario_1_order_registration(page: Page):
    """시나리오 1: 발주사 주문 등록 테스트"""
    
    # 1. 로그인 페이지로 이동
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 2. 삼성 계정으로 로그인
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    login_button = page.locator('button:has-text("로그인")').first
    
    username_input.wait_for(state="visible", timeout=15000)
    username_input.fill(SAMSUNG_USERNAME)
    time.sleep(0.5)
    password_input.fill(SAMSUNG_PASSWORD)
    time.sleep(0.5)
    login_button.click()
    
    # 로그인 후 대시보드로 이동 확인
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # 대시보드 확인
    page.wait_for_selector('h1', timeout=20000)
    page_content = page.content()
    assert "대시보드" in page_content or "발주사" in page_content, "대시보드로 이동하지 못했습니다"
    
    # 3. 주문 등록 페이지로 이동
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
    
    # 주문 등록 페이지 확인
    page_content = page.content()
    assert "주문" in page_content, "주문 등록 페이지로 이동하지 못했습니다"
    
    # 4. 수동 주문 등록 탭에서 주문 등록
    # 품목명 선택 (selectbox 찾기)
    selects = page.locator('select')
    if selects.count() > 0:
        item_select = selects.first
        # 옵션 개수 확인 후 첫 번째 실제 품목 선택
        options = item_select.locator('option')
        if options.count() > 1:
            item_select.select_option(index=1)  # 첫 번째 품목 선택
            time.sleep(2)
    
    # 주문수량 입력
    number_inputs = page.locator('input[type="number"]')
    if number_inputs.count() > 0:
        qty_input = number_inputs.first
        qty_input.clear()
        qty_input.fill("100")
        time.sleep(1)
    
    # 항목 추가 버튼 클릭
    add_buttons = page.locator('button').filter(has_text="항목 추가")
    if add_buttons.count() > 0:
        add_button = add_buttons.first
        add_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    
    # 5. 발주서 생성 및 등록
    submit_buttons = page.locator('button').filter(has_text="발주서 생성")
    if submit_buttons.count() > 0:
        submit_button = submit_buttons.first
        submit_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)
    
    # 성공 메시지 확인
    page_content = page.content()
    assert "성공" in page_content or "등록되었습니다" in page_content, "주문 등록 성공 메시지를 찾을 수 없습니다"
    
    # 6. 엑셀 업로드 탭으로 이동 (선택사항 - 엑셀 파일이 없으면 스킵)
    tabs = page.locator('button[role="tab"]')
    if tabs.count() > 1:
        excel_tab = tabs.nth(1)  # 두 번째 탭이 엑셀 업로드
        excel_tab.click()
        time.sleep(2)
        # 엑셀 파일 업로드는 실제 파일이 필요하므로 여기서는 스킵
    
    # 7. 대시보드로 이동
    dashboard_buttons = page.locator('button').filter(has_text="대시보드")
    if dashboard_buttons.count() > 0:
        dashboard_button = dashboard_buttons.first
        dashboard_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    
    # 대시보드 확인
    page_content = page.content()
    assert "대시보드" in page_content, "대시보드로 이동하지 못했습니다"
    
    # 8. 로그아웃
    logout_buttons = page.locator('button').filter(has_text="로그아웃")
    if logout_buttons.count() > 0:
        logout_button = logout_buttons.first
        logout_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    
    # 로그인 페이지로 돌아왔는지 확인
    page_content = page.content()
    assert "사용자명" in page_content or "로그인" in page_content, "로그아웃 후 로그인 페이지로 이동하지 못했습니다"
    
    print("✓ 시나리오 1 테스트 완료")

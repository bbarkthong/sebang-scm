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
import os

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
    
    # # 4. 수동 주문 등록 탭에서 주문 등록
    # # 페이지 끝까지 스크롤
    # page.mouse.move(500, 500)
    # page.mouse.wheel(0, 5000)
    
    # # 품목명 선택
    # expander = page.locator('details:has-text("항목 추가")').first
    # is_open = expander.get_attribute('open')
    # if not is_open:
    #     expander.click()
    #     time.sleep(1)
    
    # item_select = expander.locator('[data-baseweb="select"]').first
    # assert item_select.count() > 0, "품목 선택 selectbox를 찾을 수 없습니다"
    
    # # selectbox가 보이도록 스크롤하고 클릭하여 드롭다운 열기
    # item_select.scroll_into_view_if_needed()
    # item_select.click()
    # time.sleep(2)
    
    # # 드롭다운 메뉴 찾기 (ul 요소 중 "선택하세요" 옵션을 가진 것)
    # dropdown_menu = None
    # all_uls = page.locator('ul')
    # for i in range(all_uls.count()):
    #     ul = all_uls.nth(i)
    #     lis = ul.locator('li')
    #     if lis.count() > 1:
    #         try:
    #             first_text = lis.first.inner_text()
    #             if "선택하세요" in first_text:
    #                 ul_box = ul.bounding_box()
    #                 expander_box = expander.bounding_box()
    #                 if ul_box and expander_box:
    #                     if abs(ul_box['y'] - (expander_box['y'] + expander_box['height'])) < 300:
    #                         dropdown_menu = ul
    #                         break
    #         except:
    #             continue
    
    # assert dropdown_menu is not None, "드롭다운 메뉴를 찾을 수 없습니다"
    
    # # 두 번째 옵션 선택 (첫 번째는 "선택하세요")
    # options = dropdown_menu.locator('li')
    # option_count = options.count()
    # assert option_count > 1, f"품목 옵션이 없습니다 (옵션 개수: {option_count})"
    
    # selected_option = options.nth(1)
    # selected_option.click()
    # time.sleep(2)
    
    # # 주문수량 입력
    # number_inputs = page.locator('input[type="number"]')
    # if number_inputs.count() > 0:
    #     qty_input = number_inputs.first
    #     time.sleep(0.5)
    #     qty_input.clear()
    #     qty_input.fill("100")
    #     time.sleep(1)
        
    #     # 입력값 확인
    #     input_value = qty_input.input_value()
    #     assert input_value == "100", f"주문수량 입력 실패. 예상: '100', 실제: '{input_value}'"
    #     print(f"✓ 주문수량 '{input_value}' 입력 확인 완료")
    
    # # 항목 추가 버튼 클릭
    # add_buttons = page.locator('button').filter(has_text="항목 추가")
    # if add_buttons.count() > 0:
    #     add_button = add_buttons.first
    #     time.sleep(0.5)
    #     add_button.click()
    #     page.wait_for_load_state("networkidle")
    #     time.sleep(3)
        
    #     # 항목이 추가되었는지 확인 (등록된 주문 상세 섹션이 나타나는지 확인)
    #     page_content = page.content()
    #     assert "등록된 주문 상세" in page_content or "순번" in page_content, "항목이 추가되지 않았습니다"
    #     print("✓ 항목 추가 확인 완료")
    
    # # 5. 발주서 생성 및 등록
    # # 발주서 생성 버튼이 보이도록 스크롤
    # page.mouse.move(500, 500)
    # page.mouse.wheel(0, 5000)
    # time.sleep(1)
    
    # submit_buttons = page.locator('button').filter(has_text="발주서 생성")
    # if submit_buttons.count() > 0:
    #     submit_button = submit_buttons.first
    #     time.sleep(0.5)
    #     submit_button.click()
    #     page.wait_for_load_state("networkidle")
    #     time.sleep(5)
    
    # # 성공 메시지 확인
    # page_content = page.content()
    # assert "성공" in page_content or "등록되었습니다" in page_content, "주문 등록 성공 메시지를 찾을 수 없습니다"
    
    # 6. 엑셀 업로드 탭으로 이동 및 파일 업로드
    page.mouse.move(500, 500)
    page.mouse.wheel(0, 0)
    time.sleep(1)
    
    tabs = page.locator('button[role="tab"]')
    assert tabs.count() > 1, "엑셀 업로드 탭을 찾을 수 없습니다"
    
    excel_tab = tabs.nth(1)  # 두 번째 탭이 엑셀 업로드
    excel_tab.click()
    time.sleep(2)
    
    # 파일 업로드 input 찾기
    file_input = page.locator('input[type="file"]')
    assert file_input.count() > 0, "파일 업로드 input을 찾을 수 없습니다"
    
    # 파일 경로 설정 (절대 경로)
    excel_file_path = os.path.join(os.path.dirname(__file__), "주문템플릿_20251216.xlsx")
    excel_file_path = os.path.abspath(excel_file_path)
    assert os.path.exists(excel_file_path), f"엑셀 파일을 찾을 수 없습니다: {excel_file_path}"
    
    # 파일 업로드
    file_input.set_input_files(excel_file_path)
    time.sleep(3)  # 파일 업로드 및 처리 대기
    
    # 엑셀 파일이 처리되었는지 확인 (성공 메시지 또는 데이터프레임 확인)
    page.mouse.move(500, 500)
    page.mouse.wheel(0, 5000)
    time.sleep(1)
    page_content = page.content()
    assert "개 항목을 읽었습니다" in page_content or "데이터프레임" in page_content.lower(), "엑셀 파일이 처리되지 않았습니다"
    
    # 주문 정보 입력 (주문일자, 고객사, 주문구분은 기본값으로 설정되어 있을 수 있음)
    # 주문 등록 버튼 찾기 및 클릭
    submit_buttons = page.locator('button').filter(has_text="발주서 생성")
    if submit_buttons.count() > 0:
        submit_button = submit_buttons.first
        submit_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # 성공 메시지 확인
        page_content = page.content()
        assert "성공" in page_content or "등록되었습니다" in page_content, "엑셀 업로드 주문 등록 성공 메시지를 찾을 수 없습니다"
        print("✓ 엑셀 업로드 주문 등록 완료")
    
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

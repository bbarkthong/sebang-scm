"""
E2E 테스트 설정 파일
"""
import pytest
import subprocess
import time
import os
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Streamlit 서버 URL
STREAMLIT_URL = "http://localhost:8501"

@pytest.fixture(scope="session")
def streamlit_server():
    """Streamlit 서버 시작 및 종료"""
    # 서버가 이미 실행 중인지 확인
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result == 0:
        # 이미 실행 중
        print("Streamlit 서버가 이미 실행 중입니다.")
        yield
        return
    
    # Streamlit 서버 시작
    process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 서버가 시작될 때까지 대기
    max_retries = 30
    for i in range(max_retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        if result == 0:
            print(f"Streamlit 서버가 시작되었습니다. (시도 {i+1}/{max_retries})")
            break
        time.sleep(1)
    else:
        raise Exception("Streamlit 서버를 시작할 수 없습니다.")
    
    yield
    
    # 서버 종료
    process.terminate()
    process.wait()
    print("Streamlit 서버가 종료되었습니다.")

@pytest.fixture(scope="function")
def page(playwright, streamlit_server):
    """Playwright 페이지 객체 생성"""
    browser = playwright.chromium.launch(headless=False)  # 브라우저 표시
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(30000)  # 30초 타임아웃
    yield page
    page.close()
    context.close()
    browser.close()


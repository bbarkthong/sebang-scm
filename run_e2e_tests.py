#!/usr/bin/env python3
"""
E2E 테스트 실행 스크립트
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """E2E 테스트 실행"""
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("세방산업 SCM E2E 테스트 실행")
    print("=" * 60)
    
    # 1. Playwright 브라우저 설치 확인
    print("\n[1/4] Playwright 브라우저 설치 확인 중...")
    try:
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Playwright 브라우저 설치 완료")
        else:
            print("⚠ Playwright 브라우저 설치 중 경고 발생")
    except FileNotFoundError:
        print("✗ Playwright가 설치되지 않았습니다. 'pip install playwright'를 실행하세요.")
        sys.exit(1)
    
    # 2. Streamlit 서버 실행 확인
    print("\n[2/4] Streamlit 서버 확인 중...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result != 0:
        print("⚠ Streamlit 서버가 실행되지 않았습니다.")
        print("  다음 명령어로 서버를 시작하세요:")
        print("  streamlit run app.py --server.port 8501")
        response = input("\n지금 서버를 시작하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            print("Streamlit 서버 시작 중...")
            subprocess.Popen(
                ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            import time
            print("서버 시작 대기 중...")
            for i in range(30):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8501))
                sock.close()
                if result == 0:
                    print("✓ Streamlit 서버 시작 완료")
                    break
                time.sleep(1)
            else:
                print("✗ Streamlit 서버 시작 실패")
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        print("✓ Streamlit 서버 실행 중")
    
    # 3. E2E 테스트 실행
    print("\n[3/4] E2E 테스트 실행 중...")
    print("-" * 60)
    
    test_dir = project_root / "tests" / "e2e"
    pytest_args = [
        "pytest",
        str(test_dir),
        "-v",
        "-s",
        "--tb=short",
        "-m", "e2e",
        "--browser", "chromium",
        "--headed"  # 브라우저 표시 (비표시하려면 제거)
    ]
    
    result = subprocess.run(pytest_args, cwd=project_root)
    
    # 4. 결과 요약
    print("\n[4/4] 테스트 완료")
    print("=" * 60)
    
    if result.returncode == 0:
        print("✓ 모든 E2E 테스트 통과!")
    else:
        print("✗ 일부 테스트 실패")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()


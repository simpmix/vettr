import uvicorn
import sys
import webbrowser
import threading
import time
from vettr.config import SERVER_HOST, SERVER_PORT

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://{SERVER_HOST}:{SERVER_PORT}")

if __name__ == "__main__":
    print("=" * 65)
    print("  VETTR : AUTONOMOUS REGULATORY & FINANCIAL INTELLIGENCE TERMINAL")
    print(f"  Live Workstation: http://{SERVER_HOST}:{SERVER_PORT}")
    print("=" * 65)

    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("vettr.web.app:app", host=SERVER_HOST, port=SERVER_PORT, log_level="info")

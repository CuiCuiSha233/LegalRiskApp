import threading
import time
import sys
import os
import webview
import base64
import tkinter as tk
from tkinter import filedialog
from fastapi.staticfiles import StaticFiles
from backend.main_api import app as api_app

APP_VERSION = "1.1.0"

_RESET = "\033[0m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_DIM = "\033[90m"
_BOLD = "\033[1m"


def _banner():
    import platform as pf
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    plat = f"{pf.system()} {pf.release()}"
    pid = str(os.getpid())
    cwd = os.path.dirname(os.path.abspath(__file__))
    if len(cwd) > 48:
        cwd = "..." + cwd[-45:]

    art = rf"""
{_CYAN}
    ██╗     ███████╗ ██████╗  █████╗ ██╗
    ██║     ██╔════╝██╔════╝ ██╔══██╗██║
    ██║     █████╗  ██║  ███╗███████║██║
    ██║     ██╔══╝  ██║   ██║██╔══██║██║
    ███████╗███████╗╚██████╔╝██║  ██║███████╗
    ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
{_RESET}{_BOLD}    Legal Risk Analysis System v{APP_VERSION}{_RESET}
{_DIM}    LLMs Powered by Xiaomi MiMo{_RESET}
{_DIM}    Author: Yebken{_RESET}
{_DIM}────────────────────────────────────────────────{_RESET}
{_GREEN}    Python{_RESET}    {pyver}
{_GREEN}    Platform{_RESET}  {plat}
{_GREEN}    PID{_RESET}       {pid}
{_DIM}────────────────────────────────────────────────{_RESET}
"""
    print(art)


def _log(tag, msg):
    ts = time.strftime("%H:%M:%S")
    print(f"  \033[90m[{ts}]\033[0m {tag} {msg}")


class DownloadApi:
    def save_file(self, data):
        try:
            filename = data.get("filename", "file.txt")
            content = data.get("content", "")

            decoded_content = base64.b64decode(content)

            root = tk.Tk()
            root.withdraw()

            file_extension = os.path.splitext(filename)[1]
            if file_extension:
                file_types = [
                    (f"{filename.split('.')[-1].upper()} 文件", f"*{file_extension}"),
                    ("所有文件", "*"),
                ]
            else:
                file_types = [("所有文件", "*")]

            save_path = filedialog.asksaveasfilename(
                defaultextension=file_extension,
                initialfile=filename,
                filetypes=file_types,
            )

            root.destroy()

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(decoded_content)
                return {"success": True, "path": save_path}
            else:
                return {"success": False, "error": "用户取消了保存"}
        except Exception as e:
            return {"success": False, "error": str(e)}


frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    api_app.mount("", StaticFiles(directory=frontend_dist, html=True), name="static")


def start_server():
    import uvicorn
    _log("\033[36m[SERVER]\033[0m", "Starting uvicorn on \033[33mhttp://127.0.0.1:8000\033[0m")
    uvicorn.run(api_app, host="127.0.0.1", port=8000, log_level="warning", access_log=False)


def main():
    _banner()
    _log("\033[32m[启动]\033[0m", "正在初始化应用程序...")

    frontend_ok = os.path.exists(frontend_dist)
    if frontend_ok:
        fcount = sum(len(files) for _, _, files in os.walk(frontend_dist))
        _log("\033[32m[启动]\033[0m", f"前端资源: \033[32m✓ 已加载\033[0m ({fcount} 个文件)")
    else:
        _log("\033[32m[启动]\033[0m", f"前端资源: \033[31m✗ 未找到\033[0m")

    _log("\033[36m[服务器]\033[0m", "正在启动后端服务线程...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    _log("\033[33m[等待]\033[0m", "等待后端服务就绪...")
    for i in range(20):
        time.sleep(0.25)
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:8000/favicon.ico", timeout=1)
            _log("\033[36m[服务器]\033[0m", f"\033[32m✓ 服务就绪\033[0m (耗时 {(i+1)*0.25:.1f}s)")
            break
        except Exception:
            pass
    else:
        _log("\033[36m[服务器]\033[0m", "\033[33m⚠ 服务启动较慢，继续启动...\033[0m")

    download_api = DownloadApi()
    _log("\033[35m[窗口]\033[0m", "正在创建原生窗口 (1200×820)...")

    window = webview.create_window(
        "LLMs分析社交行为法律风险系统",
        "http://127.0.0.1:8000",
        width=1200,
        height=820,
        resizable=True,
        fullscreen=False,
        js_api=download_api,
    )

    _log("\033[35m[窗口]\033[0m", "\033[32m✓ 窗口创建完成\033[0m — 进入事件循环")
    _log("\033[32m[APP]\033[0m", "\033[1;32m🚀 应用启动成功!\033[0m")
    print()

    webview.start()


if __name__ == "__main__":
    main()

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

    uvicorn.run(api_app, host="127.0.0.1", port=8000)


def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    time.sleep(2)

    download_api = DownloadApi()

    window = webview.create_window(
        "LLMs分析社交行为法律风险系统",
        "http://127.0.0.1:8000",
        width=1200,
        height=820,
        resizable=True,
        fullscreen=False,
        js_api=download_api,
    )

    webview.start()


if __name__ == "__main__":
    main()

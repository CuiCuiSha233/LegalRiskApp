import os
import subprocess
import shutil

# 项目根目录
BASE_DIR = os.path.dirname(__file__)


# 清理旧的构建文件
def clean_build():
    build_dir = os.path.join(BASE_DIR, "build")
    dist_dir = os.path.join(BASE_DIR, "dist")

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    print("清理完成")


# 打包成可执行文件
def build_executable():
    # 构建命令
    cmd = [
        "pyinstaller",
        "--noconsole",  # 无黑框
        "--onefile",  # 单文件模式
        "--name",
        "LegalRiskApp",
        "--add-data",
        "frontend/dist;frontend/dist",
        "--add-data",
        "SimHei.ttf;.",
        "--add-data",
        "favicon.ico;.",
        "--icon",
        "favicon.ico",
        "main.py",
    ]

    print("开始打包...")
    subprocess.run(cmd, check=True)
    print("打包完成")


if __name__ == "__main__":
    clean_build()
    build_executable()

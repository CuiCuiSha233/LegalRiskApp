import logging
import time
import sys

TAG_MAP = {
    "api": ("API", "\033[36m"),
    "analysis": ("分析", "\033[35m"),
    "llm": ("LLM", "\033[33m"),
    "db": ("数据库", "\033[32m"),
    "error": ("错误", "\033[31m"),
    "nlp": ("NLP", "\033[96m"),
    "auth": ("认证", "\033[36m"),
    "file": ("文件", "\033[32m"),
    "export": ("导出", "\033[35m"),
}
RESET = "\033[0m"
DIM = "\033[90m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"


class AppFormatter(logging.Formatter):
    def format(self, record):
        ts = time.strftime("%H:%M:%S")
        name = record.name.lower()
        tag_label, tag_color = TAG_MAP.get(name, ("INFO", "\033[36m"))
        msg = record.getMessage()
        return f"  {DIM}[{ts}]{RESET} {tag_color}[{tag_label}]{RESET} {msg}"


_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(AppFormatter())


def get_logger(name="app"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(_handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger


def log_api(method, path, status=None, duration=None):
    logger = get_logger("api")
    status_str = ""
    if status is not None:
        if 200 <= status < 300:
            status_str = f"  {GREEN}{status}{RESET}"
        elif 400 <= status < 500:
            status_str = f"  {YELLOW}{status}{RESET}"
        else:
            status_str = f"  {RED}{status}{RESET}"
    dur_str = f"  {DIM}{duration:.0f}ms{RESET}" if duration else ""
    logger.info(f"{CYAN}{method}{RESET} {path}{status_str}{dur_str}")


def log_analysis(msg):
    get_logger("analysis").info(msg)


def log_llm(msg):
    get_logger("llm").info(msg)


def log_db(msg):
    get_logger("db").info(msg)


def log_error(msg):
    get_logger("error").error(msg)

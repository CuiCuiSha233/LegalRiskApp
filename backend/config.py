import json
import os
from pathlib import Path

# 应用配置文件
CONFIG_DIR = Path(os.path.expandvars("%APPDATA%")) / "LegalRiskApp"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 确保目录存在
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "Pro/deepseek-ai/DeepSeek-V3"
DEFAULT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

PROMPT_CONFIGS = {
    "expert1": {
        "name": "刑法专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位刑法专家，请分析以下行为是否触犯刑法，并列出可能涉及的罪名及法条依据。",
    },
    "expert2": {
        "name": "合规审查专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位合规审查专家，请从行政合规和行业监管的角度分析以下行为的合规风险，给出预防措施。",
    },
    "expert3": {
        "name": "证据分析专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位证据分析专家，请指出以下描述中可能存在的证据瑕疵或需要进一步调查的疑点。",
    },
    "summary": {
        "name": "汇总专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位资深律师和首席法官，请汇总以上三位专家的意见，进行交叉验证和冲突解决，最终为客户提供一份简洁、全面、专业的法律风险评估报告。严格注意：报告内容须直接输出，**不得包含报告出具人、日期、免责声明等任何尾部签名或脚注信息。**",
    },
}

SUMMARY_PROMPT = PROMPT_CONFIGS["summary"]["prompt"]


def get_default_config():
    return {
        "apiKey": "",
        "baseUrl": "https://api.siliconflow.cn",
        "secretKey": DEFAULT_SECRET_KEY,
        "configs": PROMPT_CONFIGS,
    }


def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        default_config = get_default_config()
        save_config(default_config)
        return default_config
    except Exception:
        return get_default_config()


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

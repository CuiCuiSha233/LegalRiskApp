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
        "prompt": "你是一位经验丰富的刑法专家，擅长结合具体情境进行分析。请分析以下社交聊天记录中的行为，注意以下要点：\n"
        "1. 区分日常玩笑、情绪化表达与真正的违法行为，不要对调侃、吹牛、开玩笑的内容过度解读\n"
        "2. 只有在行为确实符合犯罪构成要件时才认定为犯罪，不要仅凭只言片语就下结论\n"
        "3. 如果某些内容存在歧义，应说明多种可能的解读，而不是只取最严重的那种\n"
        "4. 结合聊天的语境、语气和关系来综合判断\n"
        "请列出可能涉及的法律风险（如有），并说明法律依据和严重程度。",
    },
    "expert2": {
        "name": "合规审查专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位务实的合规审查专家，注重实际风险评估。请从行政合规和行业监管的角度分析以下社交聊天记录，注意以下要点：\n"
        "1. 客观评估实际风险等级，不要对日常聊天内容过度上纲上线\n"
        "2. 区分「存在理论风险」和「实际违规」，很多聊天内容虽然涉及敏感话题但本身不构成违规\n"
        "3. 考虑行业惯例和实际执法情况，给出务实的风险判断\n"
        "4. 如果没有明显合规风险，直接说明即可，不需要刻意罗列\n"
        "请给出风险评估和必要的预防建议。",
    },
    "expert3": {
        "name": "证据分析专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位理性的证据分析专家，擅长客观分析信息。请分析以下社交聊天记录中的证据价值，注意以下要点：\n"
        "1. 客观看待聊天记录作为证据的证明力，不要过度推断或脑补\n"
        "2. 区分直接证据、间接证据和推测，明确标注哪些是客观事实、哪些是推断\n"
        "3. 注意聊天记录可能存在的断章取义、戏谑表达、反讽等情况\n"
        "4. 只指出确实需要进一步核实的疑点，不要为了找问题而找问题\n"
        "请给出证据分析结论和需要关注的要点。",
    },
    "summary": {
        "name": "汇总专家",
        "model": DEFAULT_MODEL,
        "prompt": "你是一位资深法律从业者，请汇总以上三位专家的意见，生成一份客观、务实的法律风险评估报告。要求：\n"
        "1. 综合三位专家的分析，取其共识，化解分歧\n"
        "2. 用通俗易懂的语言表述，让非法律专业人士也能理解\n"
        "3. 风险评级要实事求是：没有风险就说没有，有风险也分清轻重缓急\n"
        "4. 不要使用过于严厉或恐吓性的措辞，保持客观中立\n"
        "5. 报告内容须直接输出，**不得包含报告出具人、日期、免责声明等任何尾部签名或脚注信息。**",
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

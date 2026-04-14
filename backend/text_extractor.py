import io
import re
import docx
import json

from backend.pdf_generator import truncate_text, MAX_CONTENT_LENGTH

remove_for_analysis = [
    "source",
    "avatarKey",
    "avatars",
    "emojiMd5",
    "imgmsg_pd",
    "signature",
    "senderAvatarKey",
    "senderUsername",
]


def extract_text(file_content, file_type):
    if not file_content:
        return ""

    if file_type == "text/plain":
        return file_content.decode("utf-8", errors="ignore")

    if file_type == "application/json":
        text = file_content.decode("utf-8", errors="ignore")
        lines = text.split("\n")
        clean_lines = [l for l in lines if "base64" not in l.lower()]
        clean_text = "\n".join(clean_lines)
        clean_text = re.sub(r",(\s*[}\]])", r"\1", clean_text)
        try:
            data = json.loads(clean_text)
        except:
            return "Error: JSON格式不正确"

        if isinstance(data, dict):
            if "chat_history" in data:
                data = data["chat_history"]
            elif "messages" in data:
                data = data["messages"]
            elif "friend" in data and "chat_list" in data.get("friend", {}):
                data = data["friend"]["chat_list"]

            if isinstance(data, list):
                result = []
                for item in data:
                    if isinstance(item, dict):
                        msg_type = item.get("type", "")
                        if msg_type not in ["文本消息", "转账卡片"]:
                            continue
                        remove = remove_for_analysis.copy()
                        remove.extend([k for k in item.keys() if k.startswith("cdn")])
                        remove.extend(
                            [k for k in item.keys() if k.startswith("sec_msg")]
                        )
                        remove.extend(
                            [k for k in item.keys() if k.startswith("tmp_node")]
                        )
                        result.append(
                            {k: v for k, v in item.items() if k not in remove}
                        )
                data = result

        result = json.dumps(data, ensure_ascii=False, indent=2)
        result = truncate_text(result)
        return result

    if (
        file_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        try:
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            return f"Error reading docx: {e}"

    return f"不支持的文件类型: {file_type}"

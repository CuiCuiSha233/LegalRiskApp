import re
import json

STOP_WORDS = {
    "的",
    "了",
    "和",
    "是",
    "在",
    "有",
    "我",
    "不",
    "这",
    "个",
    "也",
    "就",
    "到",
    "说",
    "与",
    "为",
    "被",
    "而",
    "及",
    "或",
    "但",
    "可",
    "以",
    "及",
    "从",
    "将",
    "并",
    "对",
    "于",
    "等",
    "其",
    "中",
    "如",
    "所",
    "因",
    "由",
    "此",
    "进行",
    "或者",
    "以及",
    "可以",
    "对于",
    "通过",
    "根据",
    "按照",
    "关于",
    "其中",
    "上述",
    "以下",
    "任何",
    "请",
    "您",
    "我们",
    "他们",
    "她",
    "它",
    "这个",
    "那个",
    "什么",
    "怎么",
    "如何",
    "为什么",
    "如果",
    "那么",
    "因为",
    "所以",
    "但是",
    "而且",
    "并且",
    "已经",
    "正在",
    "将会",
    "可能",
    "需要",
    "应该",
    "必须",
    "能够",
    "是否",
    "没有",
    "不是",
    "而是",
    "还有",
    "除了",
    "即使",
    "虽然",
    "尽管",
    "一下",
    "一些",
    "一种",
    "一样",
    "一直",
    "一定",
    "一边",
    "一方面",
    "另一方面",
    "第",
    "之",
    "以",
    "使",
    "则",
    "把",
    "给",
    "向",
    "往",
    "令",
    "此时",
    "当时",
    "这些",
    "那些",
    "其他",
    "另外",
    "此外",
    "总之",
    "同时",
    "然后",
    "之后",
    "之前",
    "首先",
    "其次",
    "最后",
    "最终",
    "主要",
    "比较",
    "相当",
    "更加",
    "特别",
    "非常",
    "一般",
    "通常",
    "实际",
    "真正",
    "确实",
    "目前",
    "现在",
    "今天",
    "今年",
    "时候",
    "地方",
    "方式",
    "情况",
    "问题",
    "时间",
    "人",
    "事",
    "物",
    "地",
    "时",
    "微信",
    "转账",
    "红包",
    "收款",
    "付款",
    "用户名",
    "账号",
    "微信号",
    "手机号",
    "银行卡",
    "对方",
    "好友",
    "聊天记录",
    "消息",
    "文本消息",
    "图片",
    "表情",
    "语音",
    "视频",
    "文件",
    "名片",
    "小程序",
    "链接",
    "位置",
    "日期",
    "时间戳",
    "msg",
    "type",
    "content",
    "sender",
    "receiver",
    "from",
    "to",
    "createTime",
    "localId",
    "sessionId",
    "chatId",
    "userId",
    "nickname",
    "remark",
    "alias",
    "tag",
    "description",
    "area",
    "gender",
    "genderType",
    "avatar",
    "headImgUrl",
    "corpName",
    "corpFullName",
    "userName",
    "realName",
    "phoneNumber",
    "mail",
    "转账收款",
    "已收款",
    "待收款",
    "已转账",
    "金额",
    "人民币",
    "元",
    "钱",
    "senderDisplayName",
    "msgSeq",
    "timestamp",
    "isAt",
    "createTime",
    "subType",
    "ext",
    "img",
    "emoji",
    "file",
    "voice",
    "video",
    "location",
}


def extract_keywords(text, top_n=50):
    if not text:
        return []

    extra_stops = set()

    def extract_all_values(d):
        if isinstance(d, dict):
            for key, val in d.items():
                key_lower = key.lower()
                if (
                    "sender" in key_lower
                    or "nick" in key_lower
                    or "remark" in key_lower
                    or "user" in key_lower
                    or "display" in key_lower
                    or "wxid" in key_lower
                    or "chat" in key_lower
                ):
                    if val and isinstance(val, str):
                        extra_stops.add(val)
                        chinese = re.findall(r"[\u4e00-\u9fff]+", val)
                        for c in chinese:
                            extra_stops.add(c)
                        non_chinese = re.sub(r"[\u4e00-\u9fff]+", "", val).strip()
                        if non_chinese:
                            extra_stops.add(non_chinese)
                if isinstance(val, dict):
                    extract_all_values(val)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            extract_all_values(item)
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, dict):
                    extract_all_values(item)

    def extract_display_names_from_text(text):
        patterns = [
            r'"senderDisplayName"\s*:\s*"([^"]+)"',
            r'"senderNickName"\s*:\s*"([^"]+)"',
            r'"displayName"\s*:\s*"([^"]+)"',
            r'"nickName"\s*:\s*"([^"]+)"',
            r'"sender"\s*:\s*"([^"]+)"',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for val in matches:
                if val:
                    extra_stops.add(val)
                    chinese = re.findall(r"[\u4e00-\u9fff]+", val)
                    for c in chinese:
                        extra_stops.add(c)
                    non_chinese = re.sub(r"[\u4e00-\u9fff]+", "", val).strip()
                    if non_chinese:
                        extra_stops.add(non_chinese)

    try:
        data = json.loads(text)
        extract_all_values(data)
    except:
        extract_display_names_from_text(text)

    all_stops = STOP_WORDS | extra_stops

    try:
        import jieba

        jieba.setLogLevel(jieba.logging.WARNING)
        words = jieba.cut(text)
    except ImportError:
        words = re.findall(r"[\u4e00-\u9fff]+", text)

    word_freq = {}
    for word in words:
        if (
            len(word) >= 2
            and word not in all_stops
            and re.match(r"^[\u4e00-\u9fff]+$", word)
        ):
            word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [{"word": w, "count": c} for w, c in sorted_words[:top_n]]

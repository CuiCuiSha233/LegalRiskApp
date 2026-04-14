import io
import re
import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

MAX_CONTENT_LENGTH = 160000


def get_resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)


def _register_chinese_font():
    try:
        font_path = get_resource_path("SimHei.ttf")
        pdfmetrics.registerFont(TTFont("Chinese", font_path))
    except:
        try:
            pdfmetrics.registerFont(TTFont("Chinese", "Arial Unicode MS"))
        except:
            pdfmetrics.registerFont(TTFont("Chinese", "Helvetica"))


_register_chinese_font()


def clean_markdown(text):
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = re.sub(r"^\s*#+\s*", "", line).strip()
        cleaned.append(line)
    text = "\n".join(cleaned)
    text = re.sub(r"(\*\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"^\s*[-*]\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def truncate_text(text, max_chars=MAX_CONTENT_LENGTH):
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_brace = truncated.rfind("}")
    if last_brace > 0:
        return truncated[: last_brace + 1]
    return truncated


def generate_pdf_report(title, content, experts_reports):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles["Title"].fontName = "Chinese"
    styles["Title"].fontSize = 18
    styles["Title"].spaceAfter = 12
    styles["Title"].alignment = TA_CENTER
    styles["Normal"].fontName = "Chinese"
    styles["Heading2"].fontName = "Chinese"
    styles["Heading2"].fontSize = 14
    styles["Heading2"].spaceAfter = 8
    styles["Heading2"].alignment = TA_CENTER
    flowables = []
    flowables.append(Paragraph(title, styles["Title"]))
    flowables.append(Spacer(1, 18))
    flowables.append(Paragraph("最终汇总研判报告", styles["Heading2"]))
    for p in clean_markdown(content).split("\n"):
        if p.strip():
            flowables.append(Paragraph(str(p), styles["Normal"]))
        flowables.append(Spacer(1, 6))
    flowables.append(Spacer(1, 18))
    flowables.append(Paragraph("以下是三位专家模型的初步研判报告", styles["Title"]))
    flowables.append(Spacer(1, 12))
    for name, report in experts_reports.items():
        flowables.append(Paragraph(f"{name}报告", styles["Heading2"]))
        for p in clean_markdown(report).split("\n"):
            if p.strip():
                flowables.append(Paragraph(str(p), styles["Normal"]))
            flowables.append(Spacer(1, 6))
        flowables.append(Spacer(1, 12))
    doc.build(flowables)
    buffer.seek(0)
    return buffer

# LegalRiskApp

基于多 LLM 模型的社交行为法律风险分析系统。通过多个专家 AI 并行分析聊天记录，生成专业的法律风险评估报告。

## 功能特性

- **多专家并行分析**：刑法专家、合规审查专家、证据分析专家同时分析，实时流式输出
- **智能词云**：基于 jieba 分词，自动提取关键词并生成词云可视化
- **多格式导出**：支持 PDF、Word (.docx)、TXT 格式报告导出
- **历史管理**：分析报告自动保存，支持搜索、编辑标题、删除
- **用户系统**：JWT 认证，单会话控制，管理员用户管理
- **原生桌面应用**：基于 pywebview 的原生窗口体验

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Pinia |
| 后端 | FastAPI + uvicorn + SQLite/MySQL |
| AI 推理 | OpenAI 兼容 API（SiliconFlow、小米 MiMo 等） |
| 桌面 | pywebview |
| 打包 | PyInstaller |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 安装

```bash
# 克隆仓库
git clone https://github.com/CuiCuiSha233/LegalRiskApp.git
cd LegalRiskApp

# 创建虚拟环境
python -m venv legal_env
legal_env\Scripts\activate  # Windows
# source legal_env/bin/activate  # macOS/Linux

# 安装后端依赖
pip install fastapi uvicorn python-jose[cryptography] openai jieba python-docx reportlab pywebview pymysql pydantic

# 安装前端依赖
cd frontend
npm install
npm run build
cd ..
```

### 运行

```bash
python main.py
```

启动后会自动打开桌面窗口，通过设置页面配置 API Key 和模型即可开始使用。

### 打包 EXE

```bash
python build.py
```

生成的可执行文件在 `dist/LegalRiskApp.exe`。

## 配置

在应用的**设置页面**中配置：

- **API Key**：LLM 服务的 API 密钥
- **Base URL**：API 地址（如 `https://api.siliconflow.cn` 或 `https://token-plan-cn.xiaomimimo.com/v1`）
- **模型名称**：每个专家使用的模型（如 `Pro/deepseek-ai/DeepSeek-V3` 或 `mimo-v2.5-pro`）
- **提示词**：可自定义每个专家的分析角度和提示词

## 项目结构

```
LegalRiskApp/
├── main.py                 # 应用入口
├── build.py                # PyInstaller 打包脚本
├── backend/
│   ├── main_api.py         # FastAPI 路由与业务逻辑
│   ├── core.py             # LLM 调用与并行流式分析
│   ├── config.py           # 默认配置与提示词
│   ├── db.py               # 数据库连接与初始化
│   ├── logger.py           # 结构化日志系统
│   ├── keyword_extractor.py# jieba 关键词提取
│   ├── pdf_generator.py    # PDF 报告生成
│   └── text_extractor.py   # 文件文本提取
├── frontend/
│   └── src/
│       ├── components/     # Vue 组件
│       ├── store/          # Pinia 状态管理
│       └── api/            # API 接口封装
└── sql/
    └── mysql_schema.sql    # MySQL 建表脚本
```

## 许可证

本项目仅供学习研究使用。

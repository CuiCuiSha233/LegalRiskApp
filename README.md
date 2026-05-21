# LegalRiskApp

基于多 LLM 模型的社交行为法律风险分析系统。通过多个专家 AI 并行分析微信聊天记录，生成专业的法律风险评估报告。

## 功能特性

- **多专家并行分析** — 刑法专家、合规审查专家、证据分析专家同时分析，实时流式输出
- **智能词云** — 基于 jieba 分词，自动过滤停用词和用户名，提取关键词生成词云
- **多格式导出** — 支持 PDF、Word (.docx)、TXT 格式报告导出
- **历史管理** — 分析报告自动保存，支持搜索、编辑标题、删除
- **用户系统** — JWT 认证，单会话控制，管理员用户管理
- **原生桌面应用** — 基于 pywebview 的原生窗口体验
- **结构化日志** — 彩色分级日志输出，便于调试和监控

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Pinia |
| 后端 | FastAPI + uvicorn + MySQL |
| AI 推理 | OpenAI 兼容 API（SiliconFlow、小米 MiMo 等） |
| 桌面 | pywebview |
| 打包 | PyInstaller |
| 分词 | jieba |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 5.7+ / 8.0

### 1. 安装 MySQL

确保 MySQL 服务已启动，然后创建数据库并导入表结构：

```bash
# 登录 MySQL
mysql -u root -p

# 执行建表脚本（会自动创建数据库和默认管理员）
source sql/mysql_schema.sql
```

或者直接命令行导入：

```bash
mysql -u root -p < sql/mysql_schema.sql
```

默认管理员账号：`admin` / `admin123`（首次使用请修改密码）。

### 2. 配置数据库连接

在项目根目录创建 `database_config.json`：

```json
{
  "type": "mysql",
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "你的MySQL密码",
    "database": "legal_risk_app"
  }
}
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv legal_env
legal_env\Scripts\activate        # Windows
# source legal_env/bin/activate   # macOS/Linux

# 安装后端依赖
pip install fastapi uvicorn python-jose[cryptography] openai jieba python-docx reportlab pywebview pymysql pydantic

# 安装前端依赖并构建
cd frontend
npm install
npm run build
cd ..
```

### 4. 运行

```bash
python main.py
```

启动后会自动打开桌面窗口。首次使用需要在**设置页面**配置 LLM API。

### 5. 打包 EXE（可选）

```bash
python build.py
```

生成的可执行文件在 `dist/LegalRiskApp.exe`。

## 配置说明

### LLM API 配置

在应用的**设置页面**中配置：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| API Key | LLM 服务的密钥 | `sk-xxx` |
| Base URL | API 地址 | `https://api.siliconflow.cn` 或 `https://token-plan-cn.xiaomimimo.com/v1` |
| 模型名称 | 每个专家使用的模型 | `Pro/deepseek-ai/DeepSeek-V3` 或 `mimo-v2.5-pro` |
| 提示词 | 可自定义每个专家的分析角度 | 默认已内置，可按需修改 |

### 数据库配置

数据库连接信息存储在 `database_config.json`（项目根目录），格式见上方安装步骤。

### 用户系统

- 默认管理员：`admin` / `admin123`
- 注册页面可注册普通用户
- 管理员可在「用户管理」页面查看和删除用户

## 项目结构

```
LegalRiskApp/
├── main.py                    # 应用入口（pywebview + FastAPI）
├── build.py                   # PyInstaller 打包脚本
├── backend/
│   ├── main_api.py            # FastAPI 路由、认证、分析接口
│   ├── core.py                # LLM 调用、并行流式分析引擎
│   ├── config.py              # 默认提示词与系统配置
│   ├── db.py                  # MySQL 连接与表初始化
│   ├── logger.py              # 彩色结构化日志系统
│   ├── keyword_extractor.py   # jieba 分词与关键词提取
│   ├── pdf_generator.py       # PDF 报告生成（ReportLab）
│   └── text_extractor.py      # 文件文本提取（JSON/DOCX/TXT）
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Home.vue       # 主页面（分析/设置/历史/词云）
│   │   │   ├── Auth.vue       # 登录注册页
│   │   │   └── UserManagement.vue  # 管理员用户管理
│   │   ├── store/index.js     # Pinia 状态管理
│   │   ├── api/index.js       # API 接口封装（axios + SSE）
│   │   └── main.js            # Vue 路由与应用初始化
│   ├── package.json
│   └── vite.config.js
├── sql/
│   ├── mysql_schema.sql       # MySQL 建库建表 + 默认管理员
│   └── mysql_upgrade.sql      # 数据库升级脚本
├── SimHei.ttf                 # 中文字体（PDF 生成用）
├── favicon.ico                # 应用图标
└── config.json                # 运行时配置（自动生成，不入库）
```

## 默认端口

| 服务 | 地址 |
|------|------|
| 后端 API | `http://127.0.0.1:8000` |
| 前端页面 | 通过 pywebview 原生窗口访问 |

## 常见问题

**Q: 启动后白屏？**
A: 确认 `frontend/dist/` 目录存在。如果没有，先执行 `cd frontend && npm run build`。

**Q: 数据库连接失败？**
A: 检查 `database_config.json` 中的 MySQL 密码是否正确，MySQL 服务是否已启动。

**Q: 分析结果是空的？**
A: 在设置页面检查 API Key 和 Base URL 是否正确配置。

**Q: 词云出现句子而非词语？**
A: 确认已安装 jieba：`pip install jieba`。

## 许可证

本项目仅供学习研究使用。

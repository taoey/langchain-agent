# LangChain Agent 聊天助手

一个基于 Streamlit 和 LangChain 的智能对话助手，支持连接 Ollama 本地/远程模型服务，提供流畅的对话体验。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.55.0-red)

## ✨ 功能特性

### 🤖 智能对话
- 基于 LangChain 和 Ollama 的强大对话能力
- 流式输出，实时显示 AI 回复
- 支持多轮对话历史记录

### 🔌 灵活的模型连接
- **自动发现**：自动从 Ollama 服务器获取可用模型列表
- **模型切换**：通过下拉框快速切换不同模型
- **远程支持**：支持连接本地和远程 Ollama 服务器
- **手动输入**：自动获取失败时可手动输入模型名称

### ⚙️ 丰富的配置选项
- **服务器地址**：自定义 Ollama 服务器地址
- **温度调节**：控制模型输出的创意程度（0.0-1.0）
- **模型刷新**：一键刷新可用模型列表
- **历史管理**：清空对话历史功能

### 🎨 优雅的界面
- 响应式设计，适配不同屏幕
- 清晰的侧边栏配置区域
- 实时显示当前配置状态

## 📦 安装说明

### 前置要求
- Python 3.8 或更高版本
- 已安装并运行 Ollama 服务（本地或远程）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/taoey/langchain-agent.git
cd langchain-agent
```

2. **创建虚拟环境**（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置 Ollama 服务器**
   - 本地安装 Ollama：访问 [https://ollama.ai](https://ollama.ai) 下载安装
   - 启动 Ollama 服务：`ollama serve`
   - 下载模型：`ollama pull qwen3.5:4b`（或其他模型）

## 🚀 使用方法

### 启动应用

```bash
streamlit run main.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

### 配置步骤

1. **设置服务器地址**
   - 在侧边栏"Ollama 服务器"区域输入服务器地址
   - 默认地址：`http://192.168.3.25:11434`
   - 本地地址：`http://localhost:11434`

2. **选择模型**
   - 点击"🔄 刷新模型列表"按钮获取可用模型
   - 从下拉框中选择要使用的模型
   - 或手动输入模型名称

3. **调整参数**
   - 滑动"模型温度"滑块调整输出风格
   - 0.0：更严谨、确定的回答
   - 1.0：更有创意、多样化的回答

4. **开始对话**
   - 在底部输入框输入问题
   - AI 将实时流式输出回复

## 📋 配置说明

### 默认配置
```python
# 默认服务器地址
base_url = "http://192.168.3.25:11434"

# 默认模型
model = "qwen3.5:4b"

# 默认温度
temperature = 0.7
```

### 支持的模型
- Qwen 系列：qwen3.5:4b, qwen3.5:7b, qwen3.5:14b
- DeepSeek 系列：deepseek-r1:7b, deepseek-r1:8b
- 其他 Ollama 支持的模型

### Ollama API 端点
- 获取模型列表：`GET /api/tags`
- 聊天接口：`POST /api/chat`
- 流式输出：支持

## 🔧 技术栈

- **前端框架**：Streamlit 1.55.0
- **LLM 框架**：LangChain 1.2.12
- **Ollama 集成**：langchain-ollama 1.0.1
- **HTTP 请求**：requests 2.32.5
- **消息处理**：langchain-core 1.2.19

## 📝 更新日志

### v1.0.0 (2026-03-17)

#### 新增功能 ✨
- 添加 `get_available_models()` 函数，支持自动获取 Ollama 服务器上的可用模型列表
- 实现模型选择下拉框，支持动态切换不同模型
- 添加服务器地址配置输入框，支持自定义 Ollama 服务器地址
- 添加"刷新模型列表"按钮，支持手动刷新可用模型
- 添加手动输入模型名称功能，作为自动获取失败的后备方案
- 优化侧边栏布局，分为清晰的配置区域（服务器、模型、参数）
- 添加当前配置信息实时显示
- 优化清空对话历史按钮的样式和功能

#### 优化改进 🎯
- 重构会话状态管理，添加 `base_url` 和 `selected_model` 状态
- 支持页面刷新后保持选择的模型和服务器地址
- 优化 LLM 初始化逻辑，支持动态更新模型和服务器配置
- 改进错误处理，添加友好的错误提示信息
- 添加加载动画（spinner），提升用户体验
- 优化代码结构，提高可读性和可维护性

#### 技术变更 🔧
- 添加 `requests` 库导入，用于调用 Ollama API
- 使用 Ollama 的 `/api/tags` 接口获取模型列表
- 实现模型切换时自动重新初始化 LLM 实例
- 添加参数验证和异常处理

#### 依赖更新 📦
- requests==2.32.5（已包含在 requirements.txt 中）

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用开发框架
- [Ollama](https://github.com/ollama/ollama) - 本地运行大语言模型的工具
- [Streamlit](https://streamlit.io/) - 快速构建数据应用的 Python 框架

## 📧 联系方式

- 作者：taoey
- 项目链接：[https://github.com/taoey/langchain-agent](https://github.com/taoey/langchain-agent)

---

**享受与 AI 的智能对话体验！** 🤖✨
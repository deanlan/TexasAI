# TexasAI is an AI tool for Texas Hold'em Poker

# 🂡 TexasAI – AI 驱动的德州扑克助手

**TexasAI** 是一个用于分析和辅助德州扑克游戏的 AI 工具，包含：

- 🧠 后端：基于 **Python + FastAPI** 构建的 API 服务  
- 💻 前端：基于 **Next.js** 的现代 Web 应用

---

## 🛠 技术栈

| 层级   | 技术                          |
|--------|-------------------------------|
| 后端   | Python, FastAPI, Poetry       |
| 前端   | Next.js, TypeScript, npm      |

---

## 📁 项目结构

TexasAI/
├── texasgpt/ # 后端服务目录（FastAPI 项目）
├── web-app/ # 前端应用目录（Next.js 项目）



---

## ⚙️ 环境要求

请确保你的开发环境中已安装以下工具：

- ✅ Python 3.9 ~ 3.12
- ✅ [Poetry](https://python-poetry.org/)（用于 Python 依赖管理）
- ✅ Node.js 和 npm（用于前端开发）
- ✅ Git

---

## 🔐 API Key 获取

本项目依赖以下服务的 API 密钥（请自行注册）：

- [Clerk](https://www.clerk.com) – 用户身份验证
- [Supabase](https://www.supabase.com) – 数据库服务
- [Stripe](https://www.stripe.com) – 支付功能

建议将密钥保存到 `.env` 文件中，**切勿提交到 GitHub**。

---

## 🚀 快速启动

### 1️⃣ 克隆仓库

```bash
git clone <your-repository-url>
cd TexasAI

2️⃣ 启动后端服务

# 1. start backend service
- `cd texasgpt`
- `./start.sh`

3️⃣ 启动前端服务
# 2. start frontend service
- `cd web-app`
- `npm install`
- `npm run dev`


后端默认运行地址：http://localhost:5670

前端默认运行地址：http://localhost:3000

📝 License
本项目使用 MIT License 开源协议发布。
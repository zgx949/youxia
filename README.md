# 🌐 全国五星级国际酒店信息服务（MCP 插件）

本服务是为 MCP 市场量身打造的全国五星级国际酒店信息查询插件，支持模糊搜索、早餐筛选、价格排序等多种功能，适用于旅游出行、酒店比价、智能助手等场景。

---

## ✨ 功能特色

- ✅ 提供全国五星级国际酒店信息查询
- 🔍 支持酒店名称模糊搜索
- 🥣 可筛选“含早餐”房型
- 💰 自动提取含早餐与不含早餐的最低房价
- 📅 支持入住/离店日期参数（可选）
- ⚡ 高性能接口响应，符合 MCP 服务调用规范

---

## 📦 安装方式

1. 进入 MCP 控制台
2. 搜索关键词：`五星级国际酒店`
3. 点击插件并完成安装

或手动加入配置文件
```json
{
    "mcpServers": {
        "youxia": {
            "command": "uv",
            "args": [
                "run",
                "mcp-server.py"
            ],
          "env": {
            "APP_KEY": "sk-your-api-key-here",
            "APP_SECRET": "sk-your-api-secret-here",
            "BASE_URL": "sk-your-api-url-here"
          }
        }
    }
}
```

---

## 🚀 启动方式

### ✅ 本地开发运行

```bash
# 安装依赖
pip install -r requirements.txt
```


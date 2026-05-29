# ⚡ 中山顶盛储能运营看板

ZS7 & ZS8 双站储能电站在线可视化，数据每周自动更新。

## 🚀 部署步骤（5分钟完成）

### 第一步：上传到 GitHub

1. 打开 [github.com](https://github.com) 登录账号
2. 点击右上角 **+** → **New repository**
3. 仓库名填：`zs-energy-dashboard`，选 **Public**，点 **Create**
4. 将本文件夹内所有文件上传到仓库（拖拽上传即可）

### 第二步：开启 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. Source 选 **Deploy from a branch**
3. Branch 选 **main**，文件夹选 **/ (root)**
4. 点 **Save**

**约 1 分钟后**，看板地址为：
```
https://你的用户名.github.io/zs-energy-dashboard/
```

### 第三步：配置 EMS 账号（密钥）

1. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点 **New repository secret**，添加两条：

| 名称 | 值 |
|------|----|
| `EMS_PHONE` | 你的 EMS 登录手机号 |
| `EMS_PASSWORD` | 你的 EMS 登录密码 |

### 第四步：测试自动更新

1. 进入仓库 → **Actions** → **每周自动更新储能数据**
2. 点 **Run workflow** → **Run workflow**（手动触发测试）
3. 等待约 3 分钟，看板数据自动刷新

---

## 📅 自动更新计划

| 触发方式 | 时间 |
|---------|------|
| 自动运行 | 每周一 08:00（北京时间） |
| 手动触发 | 随时在 Actions 页面点击 |

---

## 📁 文件说明

```
zs-energy-dashboard/
├── index.html          # 可视化看板主页面
├── fetch_data.py       # EMS 数据采集脚本
├── data/
│   └── latest.json     # 最新数据（每周自动更新）
└── .github/
    └── workflows/
        └── weekly-update.yml  # GitHub Actions 工作流
```

---

## 🔔 可选：更新后自动通知

在 `weekly-update.yml` 最后取消注释，并在 Secrets 中添加 `WEBHOOK_URL`，支持飞书/企业微信机器人通知。

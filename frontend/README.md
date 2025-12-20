# HR Agent 前端应用

基于 React + Vite + Tailwind CSS 构建的现代化 HR 管理系统前端界面。

## 技术栈

- **React 18** - UI 框架
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Axios** - HTTP 客户端

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

### 预览生产构建

```bash
npm run preview
```

## 功能模块

- **请假管理** - 查看请假余额、申请请假
- **考勤** - 签到打卡、查询考勤记录
- **薪酬** - 查询工资和税费信息
- **政策查询** - 查询 HR 政策
- **福利** - 查看和申请福利
- **差旅** - 查询差旅政策、申请出差
- **报销** - 提交报销申请

## 配置

### API 地址配置

默认 API 地址为 `http://127.0.0.1:8000`，可以通过环境变量修改：

创建 `.env` 文件：

```env
VITE_API_URL=http://127.0.0.1:8000
```

### 代理配置

开发环境下，Vite 会自动代理 `/hr` 和 `/health` 请求到后端服务器。

配置位置：`vite.config.js`

## 项目结构

```
frontend/
├── src/
│   ├── api/          # API 服务层
│   ├── components/   # React 组件
│   ├── App.jsx       # 主应用组件
│   ├── main.jsx      # 入口文件
│   └── index.css     # 全局样式
├── index.html        # HTML 模板
├── package.json      # 依赖配置
├── vite.config.js    # Vite 配置
└── tailwind.config.js # Tailwind 配置
```

## 开发说明

- 确保后端 API 服务器已启动（`http://127.0.0.1:8000`）
- 前端会自动检测 API 连接状态
- 所有 API 请求都通过 `src/api/api.js` 统一管理


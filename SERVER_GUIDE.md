# 本地开发服务器启动指南

## 方式一：使用 Node.js（推荐）

### 1. 安装依赖
```bash
npm install
```

### 2. 启动服务器
```bash
npm start
```

服务器将在 http://localhost:9111 启动，浏览器会自动打开。

### 3. 停止服务器
在终端按 `Ctrl + C` 停止服务器。

## 方式二：使用 Python

### Python 3
```bash
python -m http.server 9111
```

### Python 2
```bash
python -m SimpleHTTPServer 9111
```

然后访问 http://localhost:9111

## 方式三：直接打开（支持离线）

直接双击 `index.html` 文件，用浏览器打开即可使用。

---

## 为什么推荐使用 HTTP 服务器？

1. ✅ **避免跨域问题**：某些浏览器特性在 file:// 协议下可能受限
2. ✅ **更接近生产环境**：模拟真实的 Web 服务环境
3. ✅ **更好的开发体验**：支持热重载、调试工具等
4. ✅ **功能完全兼容**：本工具的所有功能在 HTTP 模式下都能正常工作

## 端口说明

- 默认端口：**9111**
- 访问地址：http://localhost:9111
- 如果端口被占用，可以修改 `package.json` 中的端口号

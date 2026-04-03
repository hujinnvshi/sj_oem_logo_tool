# OEM Logo 包制作辅助工具

> 简单高效的 OEM 定制化配置工具，支持离线使用

## 📋 简介

OEM 信息配置工具是一款 Web 端的 OEM 定制化辅助工具，帮助用户快速配置产品信息、上传定制资源，并一键生成符合规范的 `oem.zip` 配置包。

**当前版本：** V3.0.5

## ✨ 主要功能

- ✅ **主题色配置** - 支持多种主题色选择（white、B1-B10、black、purple、blue 等17种主题）
- 🖼️ **登录页定制** - 上传登录页 Logo、背景图、底图等资源
- 🏠 **主界面定制** - 配置左侧栏展开/收起 Logo、标签页 Logo
- 📝 **产品信息配置** - 自定义产品名称、版本号等信息
- 📄 **许可协议管理** - 上传并配置许可协议文件
- 📦 **一键生成配置包** - 自动生成 `oem.zip` 文件（包含 `oeminfo.xlsx` 和 `images` 目录）
- 👀 **实时预览** - 支持登录页和主界面实时预览
- 💾 **数据持久化** - 基于 sessionStorage 自动保存填写内容
- 🔄 **恢复默认** - 一键恢复到默认配置

## 🚀 快速开始

### 在线使用

直接用浏览器打开 `index.html` 即可使用，支持离线模式。

### 本地部署

```bash
# 克隆仓库
git clone git@github.com:hujinnvshi/sj_oem_logo_tool.git

# 进入项目目录
cd sj_oem_logo_tool

# 使用任意静态服务器启动，例如：
# Python 3
python -m http.server 8000

# Node.js (需要安装 http-server)
npx http-server -p 8000
```

访问 `http://localhost:8000` 即可使用。

## 📸 图片资源规范

工具对上传的图片有明确的格式和尺寸要求：

| 资源类型 | 推荐尺寸 | 大小限制 | 支持格式 |
|---------|---------|---------|---------|
| 登陆页面 Logo | 238×75px | ≤500KB | PNG、SVG |
| 主界面左侧栏展开 Logo | 133×42px（高42px） | ≤500KB | PNG、SVG |
| 主界面左侧栏收起 Logo | 38×42px（高42px） | ≤500KB | PNG、SVG |
| 标签页 Logo | 32×32px | ≤500KB | PNG、SVG、ICO |
| 登录页面背景图片 | 1920×1080px | ≤1MB | PNG、SVG |
| 登录页面背景底图 | 1920×1080px | ≤500KB | PNG、SVG |

**注意：**
- B10 主题时，两个主界面 Logo 需要上传相同的图片
- 所有图片文件名会自动转换为规范命名（如 `logo.png`、`sec-logo.png` 等）

## 📦 输出说明

点击"生成 oem.zip"按钮后，将下载包含以下内容的 ZIP 文件：

```
oem.zip
├── oeminfo.xlsx          # OEM 配置信息表格
└── images/               # 图片资源目录
    ├── logo.png
    ├── sec-logo.png
    ├── collapsed-logo.png
    ├── favicon.ico
    ├── form-bg.png
    └── login-base-img.png
```

## 🛠️ 技术栈

- **前端框架：** 纯原生 JavaScript
- **样式：** CSS3
- **图标：** Font Awesome
- **依赖库：**
  - [SheetJS (XLSX)](https://github.com/SheetJS/sheetjs) - Excel 文件生成
  - [JSZip](https://github.com/Stuk/jszip) - ZIP 文件打包

## 📝 使用说明

1. **选择主题色** - 根据需要选择合适的主题色
2. **上传登录页资源** - 按规范上传 Logo 和背景图
3. **上传主界面资源** - 配置左侧栏和标签页 Logo
4. **填写产品信息** - 输入产品名称、版本号等信息
5. **配置许可协议** - 上传许可协议文件（可选）
6. **预览效果** - 使用预览按钮查看实际效果
7. **生成配置包** - 点击"生成 oem.zip"下载配置文件

## ⚠️ 注意事项

- 支持离线使用，无需网络连接
- 填写内容会自动保存在浏览器 sessionStorage 中
- 图片文件必须符合指定的尺寸和大小要求
- 生成的 ZIP 包可直接用于产品部署

## 📄 许可证

本项目采用 MIT 许可证。

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**Made with ❤️ for OEM customization**

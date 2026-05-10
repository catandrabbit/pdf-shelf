# PDF Shelf

中文说明 | [English](README.md)

一个轻量级、零依赖的本地 PDF 图书馆管理器。直接在浏览器中浏览、搜索和阅读你的 PDF 文藏。

![PDF Shelf](https://img.shields.io/badge/status-stable-green) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.8+-yellow)

## 截图预览

<div align="center">

![PDF Shelf 效果图](https://github.com/catandrabbit/pdf-shelf/blob/main/screenshot.png?raw=true)

*左侧浏览文件夹和书籍，右侧直接预览PDF内容*

</div>

> **提示**：如果您的实际效果与截图有差异，可以使用 AI Agent（如 Claude、Cursor、Copilot 等）对 `index.html` 进行优化调整，以达到更理想的视觉效果。

## 功能特性

- **零框架依赖** — 单 HTML 文件，无需构建，支持 `file://` 协议直接打开
- **文件夹层级** — 按文件夹结构浏览，带面包屑导航
- **封面墙** — 响应式网格布局，自动提取 PDF 封面缩略图
- **内嵌阅读器** — 可调节大小的侧边栏直接预览 PDF
- **阅读状态** — 标记书籍为 想读/在读/已读/收藏
- **最近阅读** — 自动记录最近打开的 20 本书
- **全文搜索** — 支持书名和作者搜索
- **分类颜色** — 按分类自动配色，视觉区分
- **自定义设置** — 设置面板支持修改标题、副标题等

## 快速开始

### 环境要求

- **Python 3.8+**（扫描器需要）
- **PyMuPDF**（可选，用于提取封面）

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install PyMuPDF
```

> 如果未安装 PyMuPDF，扫描器仍可正常工作，但不会提取封面图片。

### 第二步：配置

复制示例配置并编辑：

```bash
cp config.example.json config.json
```

编辑 `config.json`：

```json
{
  "library_dir": "/你的PDF文件夹路径",
  "app_title": "我的图书馆",
  "app_subtitle": "PDF 书籍收藏"
}
```

或跳过配置，直接在命令行指定目录。

### 第三步：扫描

```bash
# 使用 config.json
python scan.py

# 或直接指定目录
python scan.py /path/to/your/pdfs

# 带参数运行
python scan.py /path/to/pdfs --output-dir ./output
```

扫描器会：
1. 递归扫描所有 `.pdf` 文件
2. 标准化书名（移除编号前缀，提取版本/卷册信息）
3. 提取封面缩略图（需要 PyMuPDF）
4. 生成 `data.js` 和 `covers/` 目录

### 第四步：打开

用浏览器打开 `index.html`。双击即可，无需 Web 服务器。

## 配置说明

### config.json

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `library_dir` | string | `""` | PDF 图书目录路径 |
| `output_dir` | string | `"."` | `data.js` 和 `covers/` 输出目录 |
| `category_suffix` | string | `"书"` | 文件夹名以此结尾视为分类 |
| `ignore_dirs` | array | `[".obsidian", ...]` | 忽略的目录名 |
| `ignore_files` | array | `["desktop.ini", ...]` | 忽略的文件名 |
| `cover_size` | array | `[300, 400]` | 封面缩略图尺寸（像素） |
| `app_title` | string | `"PDF Shelf"` | 浏览器标签页和页眉标题 |
| `app_subtitle` | string | `"Local Digital Library"` | 页眉副标题 |

### 书名覆盖

创建 `title_overrides.json` 手动设置书名：

```json
{
  "book_0001": "自定义书名",
  "book_0042": "另一本覆盖"
}
```

书籍 ID 在扫描时输出（如 `book_0001`）。修改后需重新扫描。

### 命令行参数

```
python scan.py [library_dir] [options]

选项:
  --config, -c FILE    配置文件路径（默认: config.json）
  --output-dir, -o DIR 输出目录
```

## 项目结构

```
pdf-shelf/
├── index.html           # 网页界面（单文件，无依赖）
├── scan.py              # Python 扫描脚本
├── config.example.json  # 配置示例
├── requirements.txt     # Python 依赖
├── LICENSE              # MIT 协议
├── README.md            # 说明文档（英文）
├── README.zh-CN.md      # 说明文档（中文）
│
├── data.js              # 生成的书籍数据（已 gitignore）
├── covers/              # 生成的封面图片（已 gitignore）
└── config.json          # 个人配置（已 gitignore）
```

## 自定义

### 分类颜色

编辑 `index.html` 中的 `CATEGORY_COLORS` 对象：

```javascript
const CATEGORY_COLORS = {
    'Science': ['#2e7d32', '#43a047'],
    'History': ['#c62828', '#e53935'],
    'Novel':   ['#1565c0', '#1976d2'],
    // 根据需要添加更多分类
};
```

### 标题修改

使用页眉的 Settings 按钮，或编辑 `config.json` 后重新扫描。

## 浏览器兼容性

- Chrome / Edge（推荐）
- Firefox
- Safari

> 注意：侧边栏 PDF 预览依赖浏览器内置的 PDF 查看器。部分浏览器可能阻止 `file://` 协议加载 PDF — 遇到此情况可使用本地服务器，或点击「Open」按钮在系统 PDF 阅读器中打开。

## 使用技巧

- **增量扫描**：扫描器只创建新的封面缩略图，已有的不会重复生成
- **大型书库**：1000+ 本书运行流畅
- **便携性强**：整个文件夹可移动，只需保持 `index.html`、`scan.py` 和生成的文件在一起
- **隐私安全**：一切在本地运行，不上传任何数据

## 开源协议

[MIT](LICENSE)

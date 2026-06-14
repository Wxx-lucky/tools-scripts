# 文件格式转换工具

基于 MinerU CLI 的一键文件格式转换脚本，双击即可使用。

## 功能

| 输入格式 | 输出格式 | 说明 |
|---------|---------|------|
| PDF | Markdown (.md) | 自动识别文本型/扫描型，中文优化 |
| 图片（PNG/JPG/BMP/GIF 等） | Markdown (.md) | 内置 OCR 文字识别 |
| XLSX | JSON (.json) | MinerU 原生解析 |
| XLS（旧版 Excel） | JSON (.json) | pandas + xlrd 兜底 |
| DOCX | Markdown (.md) | Word 文档提取 |
| PPTX | Markdown (.md) | PPT 内容提取 |

## 快速开始

1. 双击 `启动转换工具.bat`
2. 输入文件路径（或直接将文件拖入命令行窗口）
3. 等待转换完成，结果生成在同目录下

## 环境依赖

- **Python 环境**: `D:\mineru-env\`（Python 3.12 + MinerU 3.2.3）
- **模型文件**: `D:\mineru-env\models\pipeline\`（需通过 `mineru-models-download` 下载）
- **配置文件**: `D:\mineru-env\mineru.json`

## 文件结构

```
工具脚本/
├── convert.py           # 核心转换脚本
├── 启动转换工具.bat      # 双击启动文件
├── .gitignore
└── README.md
```

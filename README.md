# 📖 摸鱼阅读器 (Moyu Reader)

> 一个低调的桌面悬浮阅读器，支持 TXT、EPUB、DOCX 格式，无边框 + 自动透明 + 底部进度条。外表像 Notepad，内心是阅读器。

---

## ✨ 功能特性

- **📄 多格式支持** — TXT（UTF-8/GBK 自动识别）、EPUB（zipfile 零依赖解析）、DOCX（python-docx）
- **🪟 无边框窗口** — `overrideredirect` 去标题栏，极致简洁
- **👻 鼠标透明** — 鼠标移出窗口自动半透明（alpha 0.02），移入恢复阅读
- **🎨 8 套内置主题** — 暗·灰白 / 暗·蓝灰 / Monokai / Dracula / 深·暖白 等
- **🎨 自定义颜色** — 支持色轮取色或手动输入 hex
- **✏ 自定义字体** — 内置 11 款中英文字体，也支持手动输入系统字体名
- **🔡 字号调节** — 8-48px 滑块，`+`/`-` 快捷键
- **📏 窗口缩放** — 8 方向拖拽调整大小
- **📌 置顶显示** — 始终悬浮在最上层
- **💾 阅读进度记忆** — 每个文件的阅读位置自动保存，下次打开自动恢复
- **📊 底部悬浮进度条** — 始终显示一条融入主题的细线，鼠标悬停展开完整进度条 + 百分比，点击跳转
- **⌨ 全局快捷键** — 见下方快捷键表
- **🚀 启动器窗口** — 友好的设置界面，选文件 → 选主题 → 调参数 → 开始阅读
- **📦 单文件打包** — PyInstaller 打包成单个 `.exe`，无需安装 Python

---

## ⌨ 快捷键

| 快捷键 | 功能 |
|---|---|
| `Space` / `PgDn` | 向下翻页 |
| `PgUp` | 向上翻页 |
| `T` | 下一个主题 |
| `R` | 上一个主题 |
| `+` / `=` | 增大字号 |
| `-` | 减小字号 |
| `↑` | 增加不透明度 |
| `↓` | 降低不透明度 |
| `Esc` / `Q` / `Ctrl+W` | 退出阅读 |

---

## 🔧 安装与运行

### 方法一：直接运行 exe（推荐）

从 [Releases](../../releases) 下载 `moyu_reader.exe`，双击运行即可。

### 方法二：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/moyu-reader.git
cd moyu-reader

# 2. 安装可选依赖（不装也能用 TXT 和 EPUB）
pip install -r requirements.txt

# 3. 运行
python moyu_reader.py
```

### 打包

```bash
pip install pyinstaller
pyinstaller moyu_reader.spec
# 输出在 dist/moyu_reader.exe
```

---

## 📁 项目结构

```
moyu-reader/
├── moyu_reader.py         # 源代码（~880 行，单文件）
├── moyu_reader.spec       # PyInstaller 打包配置
├── requirements.txt       # Python 依赖
├── dist/
│   └── moyu_reader.exe    # 打包后的程序
└── README.md
```

配置文件保存在：`~/.moyu_reader_config`（JSON 格式）

---

## 🛠 技术栈

- **Python 3.10+** 标准库 `tkinter` — 零外部 GUI 依赖
- **EPUB** — `zipfile` + `re` 内置解析（无需 ebooklib）
- **DOCX** — `python-docx`（可选）
- **打包** — PyInstaller，windowed 模式，约 10MB

---

## ⚠️ 免责声明

本工具仅供学习交流与合法阅读用途。请遵守所在公司/机构的规定，合理使用。

---

## 📜 License

MIT

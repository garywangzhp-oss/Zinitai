# 紫泥台 · 合同脱敏工具

[![Release](https://img.shields.io/github/v/release/garywangzhp-oss/Zinitai)](https://github.com/garywangzhp-oss/Zinitai/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-2C5F8A)](#下载)

把 Word / PDF 合同里的敏感信息（金额、证件号、账号……）自动识别并**真抹除**，
生成可对外分享的脱敏稿 + 映射表 + 审查报告。**纯本地离线，数据不出机器。**

> 「紫泥台」取自汉制「紫泥封诏」——以紫泥封缄诏书，是古代的机密文件封发仪式。
> 与这个工具要做的事同源：把合同里的敏感信息封存起来，再交出去。

---

## 下载

**不写代码、只想用：直接下打包好的 Windows 版，无需安装 Python。**

👉 **[下载最新版（Windows 64 位）](https://github.com/garywangzhp-oss/Zinitai/releases/latest)**

- 单文件绿色版，双击即用；
- 未做代码签名，SmartScreen 可能提示「未知发布者」，选择「仍要运行」即可；
- 首次冷启动需解包，约几秒。

> 想在其他平台跑、或想改代码：走下面的「从源码安装」。

## 为什么是它

- **真删除，不是遮挡** —— PDF 走 PyMuPDF redaction，把文字从内容流里移除，
  而不是盖一个黑框。实测：脱敏后原文的 CID 字形字节彻底消失，文本层与内容流都提取不到。
  docx 则是逐段重写 run，格式保留。
- **漏报优先 + 人工裁定** —— 默认全勾（将抹除），逐条过目，取消即排除；
  apply 只抹你勾过的那几处（所见即所抹）。
- **可逆** —— 映射表（占位符 ↔ 原文）就是还原接口，`restore.py` 一键换回原文。
- **纯本地** —— 无云端调用、无遥测、全程不联网。

## 从源码安装

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## 使用

### 桌面应用（推荐）

```
.venv\Scripts\pythonw.exe gui\app.py
```

选择文件 → 自动扫描 → 逐条审查（默认全勾，取消即排除）→ 执行抹除 →
打开输出文件夹取三件套（脱敏文件 / 映射表 / 审查报告）。

**还原**：空态页点「从脱敏稿还原…」，选择脱敏文件即可——自动配对同目录的
映射表，把占位符换回原文，输出 `xxx_还原.docx/pdf`。docx 逐字回填、格式保留；
PDF 原位回填，内容可还原但版式可能与原件有细微差异。

### 命令行

两步式：先 `scan` 出审查报告人工过目，再 `apply` 执行抹除。

```
:: 识别（不改文件，输出 Markdown 审查报告）
python main.py scan 合同A.pdf
python main.py scan 合同A.docx -o 报告目录

:: 抹除（生成 脱敏文件 + 映射表 + 报告）
python main.py apply 合同A.pdf
python main.py apply 合同A.docx -o 输出目录 --exclude 词库.txt

:: 还原
python restore.py 脱敏文件.docx
python restore.py a_脱敏.pdf b_脱敏.docx
```

批量：`scan` / `apply` 的输入既可以是单个文件，也可以是目录（处理目录下全部
`.docx` / `.pdf`）。批量时占位符全局编号——相同内容在不同文件里拿到相同占位符。

- `-o` 输出目录，缺省：单文件为文件所在目录，目录输入为 `<目录>\脱敏结果`
- `--exclude 词库.txt` 白名单，一行一条**原文精确匹配**，命中的不抹
  （用于排除误报，长期积累复用；`#` 开头为注释）
- `--ner` 启用可选的 NER 识别（人名/机构名），见下

### 可选：NER 人名 / 机构名

默认关闭，按已安装的后端自动启用，推理完全本地：

```
pip install spacy && python -m spacy download en_core_web_sm   # 英文
pip install hanlp                                               # 中文（模型较大）
```

## 识别范围

| | |
|---|---|
| 默认开启 | 金额（中文大写 + `¥/$/USD/€/£` 等国际货币）、身份证（含美国 SSN）、手机/座机（中 + 美式）、银行卡（Luhn + IBAN）、统一社会信用代码（含美国 EIN）、邮箱 |
| NER（可选） | 人名 / 机构名 |
| 输入格式 | 文字型 `.docx`、文字型 `.pdf` |
| 抹除方式 | PDF 用 PyMuPDF redaction **真删除**；docx 逐段替换 run、保留格式 |

## 支持与不支持

| 不支持 | 说明 |
|---|---|
| 扫描件 PDF | 检测到无文本层即报错（MVP 不做 OCR） |
| `.doc` 旧格式 | 请先另存为 `.docx` |
| 图片内文字 | 不做 OCR |
| 日期识别 | 易与案号/条款号混淆，不识别 |

注意：docx 含批注/修订时不处理，但会在报告中**警告**；PDF 抹除处留下空白，不重排版。

## 项目结构

```
detectors/    识别层：只负责"找"（正则规则 + 中文大写金额 + 可选 NER）
processors/   文档层：只负责"改"（docx 跨 run 替换 / PDF redaction / 抹后自检）
review/       审查报告与映射表输出
main.py       CLI 入口（scan / apply）
restore.py    还原入口
gui/          pywebview 桌面窗口（app.py + index.html）
tests/        合成样本生成与验证
```

## 从源码打包

```
pip install pyinstaller
python -m PyInstaller 紫泥台.spec --noconfirm
```

产物为单文件 `dist\紫泥台.exe`。

## 已知限制（MVP）

- 跨行的大写金额会漏（识别按行/按段进行）；
- PDF 中无法精确定位的命中按整行抹除（报告中有备注）；
- docx 里 `w:hyperlink` 等容器中的文字不在 `para.runs` 里，会漏识别。

## 隐私

仓库内**不含任何真实合同**。`tests/real/`、`tests/real_out/` 为本地真实合同及其
产物（映射表是明文个人信息），已在 `.gitignore` 中排除；仓库只保留
`tests/samples/` 下由 `tests/make_samples.py` 生成的合成样本。
---
name: 合同脱敏台 (Contract Redactor)
description: 检索工作台世界的本地合同脱敏工作台——冷白纸面上的一纸检索结果，命中即高亮，审查即裁定。
colors:
  paper: "#FAFAF7"
  paper-raise: "#FFFFFF"
  ink: "#1C1C1A"
  ink-2: "#56564F"
  ink-3: "#8B8B80"
  rule: "#E3E1D8"
  rule-2: "#D2CFC2"
  cinnabar: "#C03A2B"
  cinnabar-wash: "rgba(192,58,43,.10)"
  cinnabar-deep: "#9E2F22"
  seal-green: "#4A7043"
  lanulin: "#2C5F8A"
  ochre: "#96662F"
  violetgray: "#6B5B7A"
  amber: "#8A6D1F"
  err: "#9E2F22"
typography:
  display:
    fontFamily: "SimSun, 'Songti SC', 'Source Han Serif SC', 'NSimSun', serif"
    fontSize: "30px"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "0.06em"
  headline:
    fontFamily: "SimSun, 'Songti SC', 'Source Han Serif SC', 'NSimSun', serif"
    fontSize: "26px"
    fontWeight: 700
    letterSpacing: "0.14em"
  title:
    fontFamily: "'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Source Han Sans SC', sans-serif"
    fontSize: "17px"
    fontWeight: 700
    letterSpacing: "0.02em"
  original:
    fontFamily: "SimSun, 'Songti SC', 'Source Han Serif SC', 'NSimSun', serif"
    fontSize: "16.5px"
    fontWeight: 400
  counter:
    fontFamily: "'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Source Han Sans SC', sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.2
    fontFeature: "tnum"
  body:
    fontFamily: "'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Source Han Sans SC', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "'Microsoft YaHei UI', 'Microsoft YaHei', 'PingFang SC', 'Source Han Sans SC', sans-serif"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.08em"
rounded:
  sharp: "0"
spacing:
  gap: "8px"
  row: "12px"
  head: "16px"
  gutter: "22px"
components:
  button-primary:
    backgroundColor: "{colors.cinnabar}"
    textColor: "#FFFFFF"
    typography: "600 13px/1.65 'Microsoft YaHei UI', sans-serif, 0.04em 字距"
    padding: "8px 18px"
    rounded: "{rounded.sharp}"
  button-primary-hover:
    backgroundColor: "{colors.cinnabar-deep}"
    textColor: "#FFFFFF"
  button-secondary:
    backgroundColor: "{colors.paper-raise}"
    textColor: "{colors.ink}"
    typography: "13px/1.65 'Microsoft YaHei UI', sans-serif, 0.04em 字距"
    padding: "8px 18px"
    rounded: "{rounded.sharp}"
  button-secondary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    typography: "12px/1.65 'Microsoft YaHei UI', sans-serif"
    padding: "3px 12px"
  chip-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  tag-amount:
    backgroundColor: "{colors.cinnabar}"
    textColor: "#FFFFFF"
    typography: "11px/1.65 'Microsoft YaHei UI', sans-serif, 0.1em 字距"
    padding: "2px 8px 1px"
  tag-idcard:
    backgroundColor: "{colors.lanulin}"
    textColor: "#FFFFFF"
    typography: "11px/1.65 'Microsoft YaHei UI', sans-serif, 0.1em 字距"
    padding: "2px 8px 1px"
  tag-phone:
    backgroundColor: "{colors.ochre}"
    textColor: "#FFFFFF"
    typography: "11px/1.65 'Microsoft YaHei UI', sans-serif, 0.1em 字距"
    padding: "2px 8px 1px"
  tag-bank:
    backgroundColor: "{colors.seal-green}"
    textColor: "#FFFFFF"
    typography: "11px/1.65 'Microsoft YaHei UI', sans-serif, 0.1em 字距"
    padding: "2px 8px 1px"
  tag-credit:
    backgroundColor: "{colors.violetgray}"
    textColor: "#FFFFFF"
    typography: "11px/1.65 'Microsoft YaHei UI', sans-serif, 0.1em 字距"
    padding: "2px 8px 1px"
  hit-original:
    backgroundColor: "{colors.cinnabar-wash}"
    textColor: "{colors.ink}"
    typography: "16.5px/1.65 SimSun, serif"
    padding: "0 4px"
  dialog:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    width: "520px"
---

# Design System: 合同脱敏台 (Contract Redactor)

## Overview

**Creative North Star: 「一纸检索结果」**

世界名「检索工作台」：合同是语料，敏感信息是命中，审查即逐条裁定——整个界面自居为一份检索结果，而不是企业后台。构建忠实落地了这个自居：命中行是检索条目（勾选即裁定），类型标签取档案侧签色，分段计数器与命名相位带横贯案卷头，相位与计数恒在视野内（sticky 案卷头与执行栏）。

气质是冷白纸面上的墨黑台账：层次靠纸色阶（#FAFAF7 → #FFFFFF 提亮）与 1px 细规则线承担，全文件没有一条 border-radius 声明；唯一的浮出形制是模态下的细线纸垫（无模糊、无偏移的多层 box-shadow）。印泥朱红 #C03A2B 是唯一强调色，只落在相位、主按钮与命中本体这些「有决定要下」的位置。

确证的反参照：企业后台的卡片仪表盘排法（方向契约 THESIS 明拒，构建中无一处卡片网格）；带模糊或偏移的块状投影（评审期已替换为细线纸垫）。

**Key Characteristics:**
- 冷白纸 #FAFAF7 上的墨黑排版，层次靠纸色提亮与 1px 规则线，不靠阴影
- 直角世界：全文件零 border-radius 声明
- 印泥朱红 #C03A2B 是唯一强调色，只给相位、主按钮、命中本体
- 四类档案侧签色（黛蓝/赭石/苔绿/紫灰）只出现在类型标签与计数圆点
- 宋体 = 文书本体，雅黑 = 工具骨架，等宽 = 机器产物
- 计数恒可见且随相位诚实变化，一律制表数字

## Colors

档案纸与墨的冷灰白世界，一个印泥朱红做声音，四个低饱和档案色做分类注记。

### Primary
- **印泥朱红** (#C03A2B): 唯一强调色。用在相位当前态（pip 实心 + 底部 2px 划线）、主按钮、金额类型标签、命中原文的洗染底、复选框 accent-color、焦点环、扫描进度条、告警计数数字、完成印记描边——全部是决策与动作的位置。
- **朱红洗染** (rgba(192,58,43,.10)): 朱红的 10% 低强度版。给宋体原文压底（16.5px 命中原文）与文本选区；排除态撤除。
- **深朱** (#9E2F22): 朱红的按压/警示深档。主按钮 hover、链接 hover、完成印记文字、确认对话警示文字。

### Secondary (类型四色——档案侧签)
- **黛蓝** (#2C5F8A): 身份证标签。
- **赭石** (#96662F): 电话标签。构建注释明言取加深档以保证白字 4.5:1 对比。
- **苔绿** (#4A7043): 银行账号标签。
- **紫灰** (#6B5B7A): 统一社会信用代码标签。

四色只出现在两处：命中行的白字标签、案卷头每类计数位的 8px 圆点。

### Tertiary
- **琥珀注记** (#8A6D1F): 自动排除注记框（autonote）专用——机器替人做的排除用暗琥珀说话，不与人工裁定争夺朱红。

### Neutral
- **冷白纸面** (#FAFAF7): 全局底色。
- **提亮纸层** (#FFFFFF): 命中列底、行 hover/选中、次按钮底、抽屉——内容浮在纸上而不是浮在阴影上。
- **墨黑** (#1C1C1A): 正文、2px 结构边（案卷头下缘、执行栏上缘）、按钮与对话框的 1px 描边、按压态实底。
- **次级墨** (#56564F): 次级文字、标签、小注、开关与 pip 的描边。
- **弱墨** (#8B8B80): 构建注释限定「仅用于大字号或非关键处」——滚动条 hover、文件侧签小方块描边。
- **细规则线** (#E3E1D8): 一切行分隔与面板内描边（最高频的中性色）。
- **深规则线** (#D2CFC2): 稍深一档——chip 描边、注记框、虚线投放区、纸垫外圈、节段细线。

### Named Rules
**「一线朱红」The One-Cinnabar Rule.** 朱红只出现在「有决定要下」的位置：相位当前态、主按钮、命中本体（标签＋洗染＋勾选框）、焦点环、扫描进度、告警计数、完成印记。装饰性使用为零。
**「色不独行」The Never-Color-Alone Rule.** 类型与状态永不只靠颜色区分：每个标签自带文字，每类计数位带文字行，排除态追加「已排除，不抹除」文字注记。
**「四色守签」The Side-Tab Quartet Rule.** 类型四色只允许出现在白字标签与计数圆点两处；不上按钮底、不上表面、不上正文。

## Typography

**Display Font:** 宋体 SimSun（Songti SC / Source Han Serif SC / NSimSun 兜底）
**Body Font:** 微软雅黑 Microsoft YaHei UI（Microsoft YaHei / PingFang SC / Source Han Sans SC 兜底）
**Label/Mono Font:** Consolas（Courier New 兜底）——映射表与词库等机器产物专用

**Character:** 两只手分工——宋体代表文书（合同原文、文件名、空态邀请、完成印记），雅黑代表工具（一切可操作物）；宋体出现处必是纸面语义，雅黑出现处必是操作语义，等宽出现处必是机器写的东西。

### Hierarchy
- **Display** (宋体 400 · 30px · 0.06em): 空态投放区标题「把合同拖进来」——纸面邀请，刻意不用粗体。
- **Headline** (宋体 700 · 26px · 0.14em): 完成印记「抹除完成」——全系统唯一的仪式性大字。
- **Title** (雅黑 700 · 15–17px · 0.02em): 品牌「合同脱敏台」17px、对话框标题 16px、抽屉标题 15px。
- **Original** (宋体 400 · 16.5px): 命中原文——行内唯一的宋体大字，压 10% 朱红洗染。这是系统里最重要的一个字号。
- **Counter** (雅黑 700 · 19px · 制表数字): 分段计数器大数字；文件行命中数 16px、执行栏待抹计数 15px 同族。
- **Body** (雅黑 400 · 14px · 1.65): 全局正文基线；上下文 12.5px、对话框正文 13px 是其加密档。
- **Label** (雅黑 400 · 11–12px · 0.06–0.14em 字距): 计数位标签 0.08em、面板头 0.14em、相位名 13px 0.08em、类型标签 11px 0.1em 白字、位置标注 11px 制表。

### Named Rules
**「宋管纸，黑管活」The Two Hands Rule.** 宋体只给文书本体（原文、文件名、仪式字），雅黑只给工具与操作，Consolas 只给机器产物；任何新文字先问它是纸、是工具、还是机器写的。
**「数必制表」The Tabular Count Rule.** 一切数字（计数、位置、映射表）走 .num 制表数字（tabular-nums + "tnum"）；对齐的计数列是这个系统的仪表盘。

## Layout

桌面窗口 1280×800 设计，body min-width 860px，960 仍可用；≤1080px 进入紧凑档（全站唯一媒体查询：隐藏每类计数位、文件侧签 264→220px、品牌格 172→140px）。

空间模型是三段横带 + 两栏：
- **案卷头**（sticky top，下缘 2px 墨线）：品牌格｜命名相位带（方 pip + 26px 细线节段）｜右侧分段计数器与每类计数位——格与格之间全部 1px 规则线分隔。
- **主体两栏**：左文件侧签 264px 固定（头 11px/0.14em 刻度标签、滚动文件列表、底部 NER 开关与词库链接三段式），右命中列弹性占满、提亮纸层。
- **执行栏**（sticky bottom，上缘 2px 墨线）：左待抹/已排除计数，右次按钮 + 主按钮。

间距节奏（台账式密集节奏，非严格数列）：**22px 页沟**（命中栏、命中行、执行栏、注记与对话框的统一水平沟）；**16px 面板头内距**；**12–13px 行内距**；**8–10px 行内小距**；分割一律 1px。

滚动：命中列与文件列表各自内部滚动；全局滚动条也入系——10px、纸色轨、rule-2 拇指带 2px 纸边、hover 弱墨。

## Elevation & Depth

纸面世界不用投影做深度。层次由四种手段承担：①纸色阶（paper → paper-raise 提亮）；②1px 规则线；③2px 墨线做结构框；④唯一的投影形制——**细线纸垫**：多层无模糊、无偏移的 spread-only box-shadow 叠出的同心细线框，像纸上再垫一张纸边。评审期构建曾用零模糊偏移块投影，已替换为此形制；构建中仅存的 box-shadow 均属此形制。

### Shadow Vocabulary
- **细线纸垫** (`box-shadow: 0 0 0 4px var(--paper), 0 0 0 5px var(--rule-2)`): 模态对话框浮出纸面时的衬边——纸色垫一层，深规则线收一圈。
- **对话框纱** (`rgba(28,28,26,.42)` 全屏遮罩): 模态背后的墨色纱；是遮罩不是阴影。

### Named Rules
**「细线纸垫」The Hairline Mat Rule.** 深度只用无模糊、无偏移的多层细线纸垫与 1px 规则线表达；带模糊或 x/y 偏移的块状投影不进这个系统。（唯一例外：完成印记的 20% 透明错版重影是印章双印器件，仅限印记本身，见 Components。）

## Shapes

直角世界：整个构建没有任何 border-radius 声明——按钮、对话框、标签、pip、开关、滚动条全部直角。

形由描边承担，描边有明确的五级重量阶梯：
- **1px 细规则线** (rule): 行分隔、面板内框——最高频；
- **1px 深规则线** (rule-2): 交互控件描边（chip、注记框、映射表框）与纸垫外圈；
- **1px 墨线** (ink): 需要实体感的描边（按钮、对话框、抽屉左缘、开关）；
- **2px 墨线**: 结构框——一屏只有两处（案卷头下缘、执行栏上缘）；
- **2.5px 朱红**: 完成印记描边——全系统只有一处。

虚线只属于投放区（2px dashed rule-2）。小记号几何：12px 方 pip、8px 方块（文件选中记号）与 8px 圆点（计数圆点）、30×16 直角开关推 10px 方钮。

## Components

### Buttons
- **Shape:** 直角（0 radius），1px 描边。
- **Primary:** 朱红底白字 600（8px 18px · 13px · 0.04em 字距）；hover 加深为深朱。执行抹除是全页唯一常驻主按钮，按钮文案自带计数「执行抹除（23）」。
- **Secondary:** 提亮纸底墨字 1px 墨线；hover 整体反白（墨底纸字）——这个系统的按压语义是反转不是变深。disabled 0.4 透明。
- **Ghost/链接:** .linkish 12px 墨字下划线（offset 3px），hover 转深朱。

### Chips（类型筛选）
- **Style:** 1px 深规则线描边、次级墨 12px 字、透明底（3px 12px）。
- **State:** 按下（aria-pressed）墨底纸字实心反转；hover 描边与文字加深。

### Tags（类型标签）
- **Style:** 11px 白字、0.1em 字距（2px 8px 1px），五色对应五类；永远带文字。
- **State:** 排除行不撤标签，整行退到 0.45 透明、洗染撤除、追加「已排除，不抹除」注记。

### Cards / Containers
系统没有卡片。容器是「面板」：纸或提亮纸的直角矩形，1px 规则线分割，无圆角无投影。对话框 520px 纸底 1px 墨线 + 细线纸垫；词库抽屉 340px 右滑提亮纸、1px 墨线左缘。注记框（自动排除/警示/错误）统一形制：1px 描边（rule-2 或语义色）、12px 字、11–14px 内距、22px 页沟外距。

### Hit Row（命中行 · 签名组件）
15px 复选框（accent-color 朱红，勾=将抹除）｜类型标签｜宋体 16.5px 原文压 10% 朱红洗染｜右缘 11px 制表位置（正文#6 / 表格[2,2]）｜下行 12.5px 次级墨上下文，命中原文以宋体 mark 再现（无底色）。行间 1px 规则线，13px 22px 内距，hover 回落纸色。排除态：整行 0.45 透明、洗染移除、显示文字注记。每处命中可见、可反悔——所见即所抹。

### Phase Band（命名相位带）
扫描→审查→完成三个 13px/0.08em 命名相位，12px 方 pip（1.5px 次级墨描边），相位间 26px×1px 细线节段。当前态：pip 朱红实心 + 相位名转墨 + 底部 2px 朱红划线压过 2px 墨结构线；已完成：pip 墨色实心。相位靠命名与记号表达，不靠色相。

### Segmented Tally（分段计数器）
右挂案卷头，格间 1px 规则线；每格 19px/700 制表数字 + 11px/0.08em 刻度标签（已扫文件/命中/已排除）。命中格 .warn：数字转朱红——数字先于颜色告警。每类计数位：11px 行 + 8px 类型色圆点 + 右对齐 13px 数字，随相位诚实变化（空态全零、扫描给部分值）。

### Dialog（确认模态）
520px 纸底直角、1px 墨线、细线纸垫；标题 16px/700；行式清单 1px 规则线分隔、右缘 ×N 计数；警示框 1px 深规则线内 12px 深朱文字；页脚右对齐 取消（次）+ 确认（主）。

### Inputs / Fields
唯一输入是复选框与开关：复选框 accent-color 朱红（评审期已把原生蓝主题为朱红）；开关 30×16 直角描边推 10px 方钮，开启态描边与钮转墨。焦点一律 :focus-visible 2px 朱红 outline（offset 2px）；文本选区朱红洗染底深朱字。

### 完成印记（Done Stamp · memorable moment）
2.5px 朱红直角印记 rotate(-2deg) 落纸：宋体 26px/0.14em「抹除完成」+ 12px 次级墨计数；叠 20% 透明的 2px 朱红错版重影（translate(4px,3px) rotate(.6deg)）——印章双印，系统里唯一允许的偏移描边器件。前置仪式：确认抹除后 500ms 全屏白闪（#fff，0.5s ease-out 退去）。全屏反白只属于这一刻。

### 机器产物面板
映射表预览与词库列表：Consolas 12px/1.7 直角面板，1px 深规则线描边，行间 1px 细规则线——机器写的东西用机器的字体，且永不与文书宋体混排。

## Do's and Don'ts

### Do:
- **Do** 给每个计数用 .num 制表数字（tabular-nums）；计数列必须纵向对齐。
- **Do** 让每处状态有文字注记：排除有「已排除，不抹除」，自动排除有琥珀注记框，错误有错误条原文。
- **Do** 新表面沿用纸阶法：底 paper，内容浮起用 paper-raise，分割用 1px rule；需要「浮出纸面」才上细线纸垫。
- **Do** 保持 22px 页沟与 12–16px 行距的台账节奏；新栏对齐 264px 侧签 + 弹性命中列的两栏骨架。
- **Do** 把宋体留给文书本体，雅黑留给工具，Consolas 留给机器产物。
- **Do** 一切状态微过渡走 0.1–0.12s ease-out，快而轻。

### Don't:
- **Don't** 圆角。整个系统零 border-radius，新组件不得引入。
- **Don't** 用带模糊或 x/y 偏移的块状投影；深度只走细线纸垫（0 0 0 Npx 多层）与规则线（完成印记的错版重影不得挪用为通用阴影）。
- **Don't** 把朱红当装饰或品牌底色铺开；它只属于相位、主按钮、命中本体、焦点、进度与完成印记。
- **Don't** 把类型四色用于标签与计数圆点之外（不做按钮底、不做表面、不做正文色）。
- **Don't** 只靠颜色传达类型或状态——每类必须有文字标签。
- **Don't** 摆企业后台卡片仪表盘：无卡片网格、无圆角悬浮卡、无图标导航（方向契约 THESIS 明拒，构建为零）。
- **Don't** 隐藏计数或相位：案卷头与执行栏恒在视野内，计数随相位诚实变化（空态全零、扫描给部分值）。

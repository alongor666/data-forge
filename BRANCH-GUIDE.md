# 🗺️ 分支导航指南

> **再也不怕忘记分支！** 这个文档会告诉你：当前在哪个分支、应该做什么、如何切换

---

## 🚦 快速识别当前分支

### 方法1: 命令行查看

```bash
# 查看当前分支（带*的是当前分支）
git branch

# 查看所有分支（包括远程）
git branch -a

# 查看当前分支详情
git status
```

### 方法2: 查看项目特征文件

| 分支 | 特征文件 | 如果存在这个文件，说明你在这个分支 |
|------|---------|---------------------------|
| **main** | `app.py` + `templates/index.html` | Flask应用 + Python后端 |
| **gh-pages-static** | `index.html` (根目录) + `processor.js` | 纯前端 + 没有app.py |
| **vercel-deployment** | `app.py` + `vercel.json` | Vercel配置 |

### 方法3: 目录结构快速判断

```bash
# 如果看到这些文件，你在 main 分支
ls -la | grep -E "app.py|requirements.txt|templates"

# 如果看到这些文件，你在 gh-pages-static 分支
ls -la | grep -E "processor.js|app.js|index.html" | grep -v templates

# 如果看到 vercel.json，你在 vercel-deployment 分支
ls -la | grep vercel.json
```

---

## 📋 三大分支速查表

### 🔵 main 分支 - 本地开发主线

**用途**: 本地开发和测试

**技术栈**: Flask + Python + pandas

**启动命令**:
```bash
# 1. 切换到main分支
git checkout main

# 2. 安装依赖（仅首次）
pip install -r requirements.txt

# 3. 启动服务器
python app.py

# 4. 浏览器访问
open http://localhost:5001
```

**适用场景**:
- ✅ 本地开发新功能
- ✅ 测试数据处理逻辑
- ✅ 调试Python代码

**关键文件**:
```
main/
├── app.py              # 主应用文件
├── templates/
│   └── index.html      # Flask模板
├── static/
│   └── styles.css      # 样式文件
├── requirements.txt    # Python依赖
├── 处理规范.md
└── CLAUDE.md
```

**开发流程**:
```bash
# 1. 确保在main分支
git branch  # 检查当前分支

# 2. 修改代码
code app.py  # 或其他文件

# 3. 测试
python app.py

# 4. 提交
git add .
git commit -m "feat: 添加新功能"

# 5. 推送
git push origin main
```

---

### 🟢 gh-pages-static 分支 - 静态网页版

**用途**: GitHub Pages部署的纯前端版本

**技术栈**: 纯JavaScript + ExcelJS + JSZip

**启动命令**:
```bash
# 1. 切换到gh-pages-static分支
git checkout gh-pages-static

# 2. 启动本地HTTP服务器
python -m http.server 8000
# 或
npx serve

# 3. 浏览器访问
open http://localhost:8000
```

**在线访问**:
```
https://alongor666.github.io/data-forge
```

**适用场景**:
- ✅ 处理小文件（≤10MB）
- ✅ 数据隐私优先
- ✅ 无需服务器
- ✅ 快速分享给他人

**关键文件**:
```
gh-pages-static/
├── index.html          # 主页面（根目录）
├── processor.js        # 数据处理器（移植自app.py）
├── app.js              # 主应用逻辑
├── static/
│   └── styles.css      # 样式文件
├── 处理规范.md
└── README-STATIC.md    # 静态版本说明
```

**开发流程**:
```bash
# 1. 确保在gh-pages-static分支
git branch

# 2. 修改代码
code processor.js  # 或其他文件

# 3. 测试（启动HTTP服务器）
python -m http.server 8000

# 4. 浏览器测试
open http://localhost:8000

# 5. 提交
git add .
git commit -m "feat: 优化前端处理逻辑"

# 6. 推送（自动部署到GitHub Pages）
git push origin gh-pages-static
```

**⚠️ 注意**:
- 推送后等待1-2分钟，GitHub Pages会自动部署
- 不要在这个分支修改app.py（这个分支没有app.py）

---

### 🟡 vercel-deployment 分支 - Vercel云端部署

**用途**: Vercel云端服务器部署

**技术栈**: Flask + Python + Vercel Serverless

**部署方式**: 自动部署（推送即部署）

**在线访问**:
```
https://data-forge-xuechenglong.vercel.app
```

**适用场景**:
- ✅ 处理大文件（10MB - 50MB）
- ✅ 在线服务
- ✅ 需要服务器性能

**关键文件**:
```
vercel-deployment/
├── app.py              # 主应用文件
├── templates/
│   └── index.html      # Flask模板
├── vercel.json         # Vercel配置（重要！）
├── requirements.txt    # Python依赖
└── 处理规范.md
```

**开发流程**:
```bash
# 1. 切换到vercel-deployment分支
git checkout vercel-deployment

# 2. 修改代码
code app.py

# 3. 本地测试（可选）
python app.py

# 4. 提交
git add .
git commit -m "feat: 优化服务器处理逻辑"

# 5. 推送（自动触发Vercel部署）
git push origin vercel-deployment

# 6. 等待1-2分钟，访问Vercel URL查看更新
open https://data-forge-xuechenglong.vercel.app
```

**⚠️ 注意**:
- 推送后Vercel会自动部署，无需手动操作
- 不要删除或修改`vercel.json`文件

---

## 🔄 分支切换完整步骤

### 场景1: 从main → gh-pages-static

```bash
# 1. 确保main分支改动已提交
git status  # 查看是否有未提交的改动

# 2. 如果有未提交的改动，先提交
git add .
git commit -m "保存main分支的改动"

# 3. 切换到gh-pages-static
git checkout gh-pages-static

# 4. 验证切换成功
ls -la  # 应该看到 index.html processor.js app.js
git branch  # 应该在 gh-pages-static

# 5. 启动静态服务器测试
python -m http.server 8000
```

### 场景2: 从gh-pages-static → main

```bash
# 1. 确保静态分支改动已提交
git status

# 2. 如果有未提交的改动，先提交
git add .
git commit -m "保存静态分支的改动"

# 3. 切换到main
git checkout main

# 4. 验证切换成功
ls -la  # 应该看到 app.py templates/ static/
git branch  # 应该在 main

# 5. 启动Flask应用测试
python app.py
```

### 场景3: 临时切换（有未提交改动）

```bash
# 方法A: 使用stash暂存
git stash  # 暂存当前改动
git checkout 目标分支
# ... 做一些操作 ...
git checkout 原分支
git stash pop  # 恢复之前的改动

# 方法B: 强制切换（不推荐，会丢失改动）
git checkout -f 目标分支
```

---

## 📝 同步共享文件的标准流程

### 场景: 更新处理规范.md（在main分支）

```bash
# 1. 在main分支修改处理规范.md
git checkout main
code 处理规范.md
git commit -m "docs: 更新处理规范"

# 2. 推送main分支
git push origin main

# 3. 同步到gh-pages-static分支
git checkout gh-pages-static
git checkout main -- 处理规范.md
git commit -m "docs: 同步main分支的处理规范更新"
git push origin gh-pages-static

# 4. 同步到vercel-deployment分支
git checkout vercel-deployment
git checkout main -- 处理规范.md
git commit -m "docs: 同步main分支的处理规范更新"
git push origin vercel-deployment

# 5. 切回main分支
git checkout main
```

---

## 🆘 紧急救援手册

### 问题1: 忘记当前在哪个分支

```bash
# 查看当前分支
git branch

# 查看分支详情
git status

# 查看目录特征文件
ls -la | head -20
```

### 问题2: 切换分支失败（有未提交改动）

```bash
# 查看哪些文件改动了
git status

# 选项A: 提交改动
git add .
git commit -m "临时提交"

# 选项B: 暂存改动
git stash

# 然后再切换
git checkout 目标分支
```

### 问题3: 不小心在错误的分支修改了代码

```bash
# 场景：在gh-pages-static分支修改了app.py（但这个分支没有app.py）

# 1. 暂存改动
git stash

# 2. 切换到正确的分支
git checkout main

# 3. 恢复改动
git stash pop
```

### 问题4: 想看其他分支的文件，但不想切换

```bash
# 查看其他分支的文件内容（不切换分支）
git show gh-pages-static:processor.js
git show main:app.py

# 对比两个分支的文件差异
git diff main..gh-pages-static -- 处理规范.md
```

### 问题5: 想回到main分支，但忘记之前做了什么

```bash
# 查看最近的提交历史
git log --oneline -5

# 查看工作目录状态
git status

# 直接切换（如果没有未提交改动）
git checkout main
```

---

## 📊 分支使用决策树

```
开始
├─ 需要开发新功能？
│  ├─ 是Python后端功能 → 使用 main 分支
│  └─ 是前端JavaScript功能 → 使用 gh-pages-static 分支
│
├─ 需要测试功能？
│  ├─ 本地测试 → main 分支
│  ├─ 在线测试（小文件） → gh-pages-static 分支
│  └─ 在线测试（大文件） → vercel-deployment 分支
│
├─ 需要部署上线？
│  ├─ GitHub Pages → gh-pages-static 分支
│  └─ Vercel云端 → vercel-deployment 分支
│
└─ 修改共享文档（如处理规范.md）？
   └─ 在 main 分支修改，然后同步到其他分支
```

---

## 🎯 每日开发检查清单

### 开始工作前

- [ ] `git branch` - 确认当前分支
- [ ] `git status` - 查看工作目录状态
- [ ] `git pull origin 当前分支` - 拉取最新代码

### 工作中

- [ ] 定期 `git status` - 查看改动文件
- [ ] 阶段性提交 `git add . && git commit -m "消息"`

### 结束工作前

- [ ] `git status` - 确保所有改动已提交
- [ ] `git push origin 当前分支` - 推送到远程
- [ ] 记录当前在哪个分支，明天继续

---

## 🔖 快捷命令别名（可选）

在 `~/.gitconfig` 或 `~/.zshrc` 中添加：

```bash
# Git别名
alias gs='git status'
alias gb='git branch'
alias gco='git checkout'
alias gcm='git checkout main'
alias gcs='git checkout gh-pages-static'
alias gcv='git checkout vercel-deployment'
alias gl='git log --oneline -10'

# 查看当前分支
alias current-branch='git rev-parse --abbrev-ref HEAD'

# 快速切换并拉取
alias switch-main='git checkout main && git pull'
alias switch-static='git checkout gh-pages-static && git pull'
alias switch-vercel='git checkout vercel-deployment && git pull'
```

使用示例：
```bash
gb          # 查看分支
gcm         # 切换到main
gcs         # 切换到gh-pages-static
```

---

## 📌 重要提醒

### ⚠️ 绝对不要做的事

1. **不要在gh-pages-static分支修改app.py** - 这个分支没有app.py
2. **不要在main分支修改processor.js** - 这个文件只在静态分支
3. **不要直接修改vercel.json** - 除非你清楚后果
4. **不要强制推送 `git push -f`** - 会覆盖远程历史

### ✅ 应该做的事

1. **切换分支前先提交** - `git status` 检查
2. **定期推送到远程** - 避免本地丢失
3. **共享文件从main同步** - 保持一致性
4. **测试后再推送** - 确保代码可运行

---

## 🎓 学习路径

### 新手（第1-2周）

1. 熟悉 `git branch` 和 `git checkout`
2. 练习在main和gh-pages-static之间切换
3. 理解每个分支的用途

### 进阶（第3-4周）

1. 掌握 `git stash` 暂存改动
2. 学会同步共享文件
3. 理解分支合并（如果需要）

### 高级（第5周+）

1. 使用Git别名提高效率
2. 熟练多分支并行开发
3. 自定义工作流程

---

## 💡 实用技巧

### 技巧1: 在命令行提示符显示当前分支

修改 `~/.zshrc` 或 `~/.bashrc`:

```bash
# 显示Git分支
parse_git_branch() {
  git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
}

# 彩色提示符
export PS1="\[\033[32m\]\w\[\033[33m\]\$(parse_git_branch)\[\033[00m\] $ "
```

效果：
```
~/Desktop/数据处理器/data-forge (main) $
~/Desktop/数据处理器/data-forge (gh-pages-static) $
```

### 技巧2: 使用VS Code显示分支

VS Code底部状态栏会显示当前分支，点击可快速切换：

![VS Code分支显示](左下角显示分支名)

### 技巧3: 创建分支切换备忘录

在项目根目录创建 `.branch-memo` 文件：

```bash
# 当前分支: main
# 任务: 修复字段映射bug
# 下次: 记得同步处理规范.md到其他分支
```

---

## 📞 需要帮助？

### 快速自查

1. `git branch` - 我在哪个分支？
2. `ls -la` - 这个分支有什么文件？
3. `git status` - 我改了什么？
4. 查看本文档 - 这个分支应该做什么？

### 常用命令速查

| 需求 | 命令 |
|------|------|
| 查看当前分支 | `git branch` |
| 切换分支 | `git checkout 分支名` |
| 查看状态 | `git status` |
| 查看改动 | `git diff` |
| 暂存改动 | `git stash` |
| 恢复暂存 | `git stash pop` |
| 查看历史 | `git log --oneline -10` |

---

**保存这个文档！** 随时查阅，永远不迷路 🧭

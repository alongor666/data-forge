# 🗺️ 分支可视化地图

> **一图胜千言** - 永远知道你在哪里，应该去哪里

---

## 📍 三大分支全景图

```
data-forge 项目
│
├─ 🔵 main                    (本地开发主线)
│  │
│  ├─ 技术栈: Flask + Python + pandas
│  ├─ 运行方式: python app.py
│  ├─ 访问: http://localhost:5001
│  │
│  ├─ 核心文件:
│  │  ├─ app.py ⭐ (主应用)
│  │  ├─ templates/index.html
│  │  ├─ static/styles.css
│  │  ├─ requirements.txt
│  │  ├─ 处理规范.md
│  │  └─ CLAUDE.md
│  │
│  ├─ 用途:
│  │  ✅ 本地开发
│  │  ✅ 测试新功能
│  │  ✅ Python后端逻辑
│  │
│  └─ 命令:
│     git checkout main
│     python app.py
│
│
├─ 🟢 gh-pages-static          (GitHub Pages部署)
│  │
│  ├─ 技术栈: 纯JavaScript + ExcelJS + JSZip
│  ├─ 运行方式: python -m http.server 8000
│  ├─ 访问: https://alongor666.github.io/data-forge
│  │
│  ├─ 核心文件:
│  │  ├─ index.html ⭐ (根目录主页)
│  │  ├─ processor.js ⭐ (数据处理器)
│  │  ├─ app.js (主逻辑)
│  │  ├─ static/styles.css
│  │  ├─ 处理规范.md
│  │  └─ README-STATIC.md
│  │
│  │  ⚠️ 没有: app.py, templates/, requirements.txt
│  │
│  ├─ 用途:
│  │  ✅ 纯前端处理
│  │  ✅ 小文件(<10MB)
│  │  ✅ 数据隐私优先
│  │  ✅ 无需服务器
│  │
│  └─ 命令:
│     git checkout gh-pages-static
│     python -m http.server 8000
│
│
└─ 🟡 vercel-deployment        (Vercel云端部署)
   │
   ├─ 技术栈: Flask + Python + Vercel Serverless
   ├─ 运行方式: 自动部署
   ├─ 访问: https://data-forge-xuechenglong.vercel.app
   │
   ├─ 核心文件:
   │  ├─ app.py ⭐
   │  ├─ templates/index.html
   │  ├─ vercel.json ⭐⭐ (部署配置)
   │  ├─ requirements.txt
   │  ├─ static/styles.css
   │  └─ 处理规范.md
   │
   ├─ 用途:
   │  ✅ 在线服务
   │  ✅ 大文件(10-50MB)
   │  ✅ 云端处理
   │
   └─ 命令:
      git checkout vercel-deployment
      git push origin vercel-deployment
      (自动部署到Vercel)
```

---

## 🔄 分支切换流程图

```
                   ┌──────────────────┐
                   │  当前在哪个分支？  │
                   └────────┬─────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
      │  main   │    │ static  │    │ vercel  │
      └────┬────┘    └────┬────┘    └────┬────┘
           │               │               │
           │         想去哪个分支？           │
           │               │               │
           └───────────────┼───────────────┘
                           │
                   ┌───────▼────────┐
                   │ git checkout   │
                   │   目标分支      │
                   └───────┬────────┘
                           │
                   ┌───────▼────────┐
                   │  验证切换成功   │
                   │  git branch    │
                   │  ls -la        │
                   └────────────────┘
```

---

## 🎯 场景导航图

### 场景1: 我要本地开发新功能

```
开始
  │
  ├─ 功能类型？
  │   ├─ Python后端 ────────────────┐
  │   └─ JavaScript前端 ──────────┐ │
  │                               │ │
  ▼                               ▼ ▼
git checkout gh-pages-static    git checkout main
  │                               │
  ├─ 启动HTTP服务器               ├─ 安装依赖(首次)
  │  python -m http.server 8000  │  pip install -r requirements.txt
  │                               │
  ├─ 修改代码                      ├─ 修改代码
  │  processor.js / app.js       │  app.py
  │                               │
  ├─ 浏览器测试                    ├─ 启动Flask
  │  localhost:8000              │  python app.py
  │                               │
  ├─ 提交                         ├─ 浏览器测试
  │  git commit                  │  localhost:5001
  │                               │
  └─ 推送                         ├─ 提交
     git push                    │  git commit
                                 │
                                 └─ 推送
                                    git push
```

### 场景2: 我要部署上线

```
部署目标？
  │
  ├─ GitHub Pages (免费静态托管)
  │   │
  │   ├─ 1. 确保在gh-pages-static分支
  │   │    git checkout gh-pages-static
  │   │
  │   ├─ 2. 推送到GitHub
  │   │    git push origin gh-pages-static
  │   │
  │   ├─ 3. 在GitHub启用Pages
  │   │    Settings → Pages → Source: gh-pages-static
  │   │
  │   └─ 4. 等待1-2分钟，访问
  │        https://alongor666.github.io/data-forge
  │
  └─ Vercel (云端服务器)
      │
      ├─ 1. 确保在vercel-deployment分支
      │    git checkout vercel-deployment
      │
      ├─ 2. 推送到GitHub
      │    git push origin vercel-deployment
      │
      ├─ 3. Vercel自动部署(无需操作)
      │
      └─ 4. 等待1-2分钟，访问
           https://data-forge-xuechenglong.vercel.app
```

### 场景3: 我要更新处理规范.md

```
1. 在main分支修改
   ├─ git checkout main
   ├─ 修改 处理规范.md
   ├─ git commit -m "docs: 更新处理规范"
   └─ git push origin main

2. 同步到gh-pages-static
   ├─ git checkout gh-pages-static
   ├─ git checkout main -- 处理规范.md
   ├─ git commit -m "docs: 同步处理规范"
   └─ git push origin gh-pages-static

3. 同步到vercel-deployment
   ├─ git checkout vercel-deployment
   ├─ git checkout main -- 处理规范.md
   ├─ git commit -m "docs: 同步处理规范"
   └─ git push origin vercel-deployment

4. 回到main分支
   └─ git checkout main
```

---

## 📊 文件对比矩阵

| 文件/目录 | main | gh-pages-static | vercel-deployment |
|-----------|------|-----------------|-------------------|
| app.py | ✅ | ❌ | ✅ |
| index.html (根目录) | ❌ | ✅ | ❌ |
| templates/index.html | ✅ | ❌ | ✅ |
| processor.js | ❌ | ✅ | ❌ |
| app.js | ❌ | ✅ | ❌ |
| static/styles.css | ✅ | ✅ | ✅ |
| requirements.txt | ✅ | ❌ | ✅ |
| vercel.json | ❌ | ❌ | ✅ |
| 处理规范.md | ✅ | ✅ | ✅ |
| CLAUDE.md | ✅ | ✅ | ✅ |

**图例**:
- ✅ 该分支有此文件
- ❌ 该分支没有此文件

---

## 🚦 快速识别当前分支

### 方法1: 看命令行提示符

如果配置了Git提示符，会显示：
```bash
~/data-forge (main) $
~/data-forge (gh-pages-static) $
~/data-forge (vercel-deployment) $
```

### 方法2: 运行一行命令

```bash
# 显示当前分支并列出特征文件
git branch | grep '*' && ls -la | grep -E "app.py|processor.js|vercel.json" | head -3
```

**输出示例**:

```bash
# 如果在 main 分支
* main
-rw-r--r--  1 user  staff   15234 Jan  1 12:00 app.py

# 如果在 gh-pages-static 分支
* gh-pages-static
-rw-r--r--  1 user  staff    8234 Jan  1 12:00 processor.js
-rw-r--r--  1 user  staff    6234 Jan  1 12:00 app.js

# 如果在 vercel-deployment 分支
* vercel-deployment
-rw-r--r--  1 user  staff   15234 Jan  1 12:00 app.py
-rw-r--r--  1 user  staff     523 Jan  1 12:00 vercel.json
```

### 方法3: VS Code底部状态栏

看VS Code左下角的分支图标：
```
🌿 main
🌿 gh-pages-static
🌿 vercel-deployment
```

---

## 🎨 分支颜色编码（可选）

在终端配置文件中设置颜色：

```bash
# ~/.zshrc 或 ~/.bashrc

# 根据分支显示不同颜色
git_branch_color() {
  local branch=$(git branch 2>/dev/null | grep '*' | sed 's/* //')

  case "$branch" in
    main)
      echo -e "\033[34m(main)\033[0m"  # 蓝色
      ;;
    gh-pages-static)
      echo -e "\033[32m(static)\033[0m"  # 绿色
      ;;
    vercel-deployment)
      echo -e "\033[33m(vercel)\033[0m"  # 黄色
      ;;
    *)
      echo -e "\033[90m($branch)\033[0m"  # 灰色
      ;;
  esac
}

# 应用到提示符
export PS1='\w $(git_branch_color) $ '
```

效果：
```bash
~/data-forge (main) $      # main显示蓝色
~/data-forge (static) $    # static显示绿色
~/data-forge (vercel) $    # vercel显示黄色
```

---

## 🔍 诊断工具

### 创建一个分支诊断脚本

创建文件 `check-branch.sh`:

```bash
#!/bin/bash

echo "🔍 分支诊断报告"
echo "=================="
echo ""

# 当前分支
current=$(git rev-parse --abbrev-ref HEAD)
echo "📍 当前分支: $current"
echo ""

# 分支特征文件检查
echo "📁 特征文件检查:"
if [ -f "app.py" ]; then
  echo "   ✅ app.py (Flask应用)"
fi

if [ -f "processor.js" ]; then
  echo "   ✅ processor.js (前端处理器)"
fi

if [ -f "vercel.json" ]; then
  echo "   ✅ vercel.json (Vercel配置)"
fi

if [ -f "index.html" ] && [ ! -d "templates" ]; then
  echo "   ✅ index.html (根目录静态页面)"
fi

if [ -d "templates" ]; then
  echo "   ✅ templates/ (Flask模板目录)"
fi

echo ""

# 分支判断
echo "🎯 分支判断:"
if [ -f "app.py" ] && [ ! -f "vercel.json" ]; then
  echo "   你在 main 分支 (本地开发)"
elif [ -f "processor.js" ] && [ -f "app.js" ]; then
  echo "   你在 gh-pages-static 分支 (静态网页)"
elif [ -f "app.py" ] && [ -f "vercel.json" ]; then
  echo "   你在 vercel-deployment 分支 (云端部署)"
else
  echo "   ⚠️  无法识别，请手动检查"
fi

echo ""

# 工作目录状态
echo "📊 工作目录状态:"
git status -s | head -5

echo ""
echo "=================="
echo "运行 'git branch' 查看所有分支"
echo "运行 'git checkout 分支名' 切换分支"
```

使用方法：
```bash
# 添加执行权限
chmod +x check-branch.sh

# 运行诊断
./check-branch.sh
```

---

## 💡 记忆技巧

### 口诀记忆法

```
🔵 main - 蓝色主线，本地开发
🟢 static - 绿色安全，纯前端运行
🟡 vercel - 黄色警示，云端部署谨慎
```

### 关联记忆法

| 分支 | 关键词 | 启动命令 | 记忆点 |
|------|--------|---------|--------|
| main | **Flask** | `python app.py` | Main = **主**应用 |
| gh-pages-static | **HTML** | `python -m http.server` | Static = **静**态页面 |
| vercel-deployment | **Vercel** | `git push` | Deployment = **部**署上线 |

### 视觉记忆法

```
main 分支 = 🏠 家 (本地)
  └─ 你在家里开发，舒适安全

gh-pages-static 分支 = 📄 展板 (展示)
  └─ 静态展板给别人看

vercel-deployment 分支 = ☁️ 云 (远程)
  └─ 部署到云端，对外服务
```

---

## 🎓 练习题

### 练习1: 快速识别

不运行任何命令，仅看以下文件列表，判断在哪个分支：

```
app.py
templates/
static/
requirements.txt
处理规范.md
```

**答案**: main分支

---

```
index.html
processor.js
app.js
static/
README-STATIC.md
```

**答案**: gh-pages-static分支

---

```
app.py
templates/
vercel.json
requirements.txt
处理规范.md
```

**答案**: vercel-deployment分支

---

### 练习2: 切换流程

假设你当前在main分支，要切换到gh-pages-static分支测试前端，写出完整步骤：

<details>
<summary>点击查看答案</summary>

```bash
# 1. 检查当前状态
git status

# 2. 如有未提交改动，先提交
git add .
git commit -m "保存main分支改动"

# 3. 切换到gh-pages-static
git checkout gh-pages-static

# 4. 验证切换成功
git branch
ls -la | grep processor.js

# 5. 启动测试服务器
python -m http.server 8000

# 6. 浏览器访问
open http://localhost:8000
```

</details>

---

## 📞 紧急救援卡

### 我完全迷失了，不知道自己在哪

```bash
# 运行这三行命令
git branch           # 查看当前分支
ls -la | head -15    # 查看文件列表
git status           # 查看工作状态

# 然后对照本文档的"文件对比矩阵"
```

### 我想回到main分支，不管现在在哪

```bash
# 如果有未保存的改动
git stash

# 切换到main
git checkout main

# 验证
git branch
ls -la | grep app.py  # 应该能看到app.py
```

### 我不小心在错误的分支修改了代码

```bash
# 不要慌！改动还在，只是分支不对

# 1. 暂存当前改动
git stash

# 2. 切换到正确的分支
git checkout 正确的分支

# 3. 恢复改动
git stash pop

# 4. 正常提交
git add .
git commit -m "在正确的分支提交"
```

---

## 🎯 总结：永远记住这5点

1. **main** = 本地开发 = 有`app.py`
2. **gh-pages-static** = 纯前端 = 有`processor.js`
3. **vercel-deployment** = 云端部署 = 有`vercel.json`
4. **切换前先提交** = `git status`检查
5. **迷路了就查这个文档** = 永远有答案

---

**收藏本文档！** 贴在显示器旁边 📌

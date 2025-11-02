# GitHub仓库设置指南

## 🎯 目标
创建GitHub仓库并配置自动化Vercel部署

## 📋 步骤

### 1. 创建GitHub仓库

#### 方法一：通过GitHub网站
1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" -> "New repository"
3. 填写仓库信息：
   - **Repository name**: `data-forge`
   - **Description**: `车险变动成本数据处理器 - 智能Excel转CSV工具`
   - **Visibility**: Public（免费）
   - **Initialize**: 不要勾选任何选项
4. 点击 "Create repository"

#### 方法二：通过GitHub CLI
```bash
# 安装GitHub CLI（如果未安装）
# brew install gh  # macOS
# apt install gh   # Ubuntu

# 登录
gh auth login

# 创建仓库
gh repo create data-forge --public --description "车险变动成本数据处理器 - 智能Excel转CSV工具"
```

### 2. 本地Git配置

#### 检查Git配置
```bash
# 检查Git是否已安装
git --version

# 配置用户信息（如果未配置）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 初始化本地仓库
```bash
# 进入项目目录
cd /Users/xuechenglong/Library/CloudStorage/GoogleDrive-alongor0512@gmail.com/其他计算机/Mac mini（公司）/Desktop/数据处理器/data-forge

# 初始化Git仓库
git init

# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/your-username/data-forge.git
```

### 3. 代码提交

#### 添加文件到暂存区
```bash
# 添加所有文件
git add .

# 或者选择性添加
git add app.py vercel_app.py vercel.json requirements.txt templates/ static/
git add *.md *.txt
```

#### 提交代码
```bash
# 创建初始提交
git commit -m "🎉 Initial commit: Data Forge - 车险变动成本数据处理器

- Flask Web应用，支持Excel文件处理
- 智能字段映射和数据转换
- Vercel Serverless部署优化
- 批量文件上传和处理
- 27个标准字段规范输出"

# 推送到GitHub
git push -u origin main
```

### 4. 分支管理

#### 创建开发分支
```bash
# 创建开发分支
git checkout -b develop

# 推送到远程
git push origin develop

# 切换回主分支
git checkout main
```

#### 标签管理
```bash
# 创建版本标签
git tag -a v3.0.0 -m "Vercel部署优化版本"
git push origin v3.0.0
```

### 5. GitHub仓库配置

#### 仓库设置
1. 进入仓库页面 -> "Settings"
2. 配置以下选项：
   - **Options**: 
     - 启用 "Issues"
     - 启用 "Projects"
     - 启用 "Wiki"（可选）
   - **Manage access**: 添加协作者（如果需要）
   - **Branches**: 设置分支保护规则

#### 添加README
如果还没有README文件，创建：
```bash
# 创建README（如果还没有）
cp README.md README_GITHUB.md
```

#### 添加开源许可证
```bash
# 创建MIT许可证
cat > LICENSE << EOF
MIT License

Copyright (c) 2025 Data Forge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### 6. Vercel集成配置

#### 安装Vercel GitHub集成
1. 访问 [Vercel GitHub集成页面](https://github.com/apps/vercel)
2. 点击 "Configure"
3. 选择要授权的仓库或 "All repositories"
4. 保存配置

#### 通过Vercel Dashboard连接
1. 登录 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 选择 "Import Git Repository"
4. 找到 `data-forge` 仓库
5. 点击 "Import"
6. 配置项目：
   - Framework Preset: Flask
   - Root Directory: `./`
   - Build Command: `echo "No build step required"`
   - Output Directory: `./`
7. 点击 "Deploy"

### 7. 自动化部署

#### 启用自动部署
Vercel默认启用自动部署：
- 每次推送到`main`分支自动触发部署
- 部署状态会显示在GitHub的Commit状态中
- 可以在Pull Request中预览部署效果

#### 部署状态检查
```bash
# 查看远程仓库信息
git remote -v

# 检查最新提交
git log --oneline -5

# 查看分支状态
git status
```

### 8. 验证部署

#### 检查部署状态
1. 访问Vercel Dashboard查看部署状态
2. 检查部署日志是否有错误
3. 访问提供的 `.vercel.app` 域名测试功能

#### 功能测试
```bash
# 测试健康检查端点
curl https://your-app.vercel.app/health

# 测试主页
curl https://your-app.vercel.app/
```

## 🔧 常用Git命令

### 日常开发
```bash
# 查看状态
git status

# 添加修改
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到远程
git push

# 拉取最新代码
git pull origin main
```

### 分支操作
```bash
# 创建并切换分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

### 版本管理
```bash
# 查看提交历史
git log --oneline

# 创建标签
git tag -a v1.0.0 -m "版本1.0.0"

# 推送标签
git push origin v1.0.0

# 查看标签
git tag
```

## 🚨 注意事项

### 敏感信息
- 不要将API密钥、密码等敏感信息提交到仓库
- 使用环境变量存储敏感配置
- 在 `.gitignore` 中排除敏感文件

### 大文件处理
- GitHub限制单文件大小为100MB
- 使用Git LFS处理大文件（如测试数据）
- 考虑使用云存储存放大型测试文件

### 分支策略
- `main` 分支：稳定版本，可直接部署
- `develop` 分支：开发版本，集成测试
- `feature/*` 分支：新功能开发
- `hotfix/*` 分支：紧急修复

## 📞 问题排查

### 推送失败
```bash
# 强制推送（谨慎使用）
git push -f origin main

# 重置远程分支
git push --force-with-lease origin main
```

### 合并冲突
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add .
git commit -m "解决合并冲突"
```

### 回退版本
```bash
# 查看提交历史
git log

# 回退到指定版本
git reset --hard <commit-hash>

# 强制推送到远程
git push -f origin main
```

---

完成这些步骤后，您的代码就会在GitHub上，并且Vercel会自动部署每次更新！

**下一步**: [Vercel部署指南](VERCEL_DEPLOYMENT.md)
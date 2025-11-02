# 🚀 立即部署指南

## 选择您的部署方式

### 🎯 方式一：一键部署（推荐）
**适合：有GitHub账号，想快速部署**

### 🔧 方式二：手动部署
**适合：想详细了解部署过程**

---

## 🎯 一键部署步骤

### 第1步：准备GitHub仓库
```bash
# 在本地项目目录执行
git remote -v  # 查看当前远程仓库

# 如果没有远程仓库，创建GitHub仓库后执行：
git remote add origin https://github.com/您的用户名/data-forge.git
git branch -M main
git push -u origin main
```

### 第2步：点击部署按钮
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/您的用户名/data-forge)

### 第3步：完成部署
1. 授权Vercel访问GitHub
2. 保持默认设置
3. 点击"Deploy"等待完成
4. 获得您的专属URL

---

## 🔧 手动部署步骤

### 第1步：创建GitHub仓库
1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `data-forge`
   - Description: `车险变动成本数据处理器`
   - 选择 "Public"
   - **不要**勾选 "Initialize this repository"
4. 点击 "Create repository"

### 第2步：推送代码到GitHub
```bash
# 在您的项目目录执行
git init
git add .
git commit -m "Initial commit: Data Forge应用"

# 添加远程仓库（替换为您的仓库URL）
git remote add origin https://github.com/您的用户名/data-forge.git
git branch -M main
git push -u origin main
```

### 第3步：Vercel部署
1. 访问 https://vercel.com
2. 使用GitHub账号登录
3. 点击 "New Project"
4. 选择 "Import Git Repository"
5. 找到您的 `data-forge` 仓库
6. 点击 "Import"
7. Framework Preset 选择 "Flask"
8. 保持其他默认设置
9. 点击 "Deploy"

---

## 📋 部署验证

### 测试部署是否成功
```bash
# 替换为您的实际URL
curl https://data-forge-您的域名.vercel.app/health
```

应该返回：
```json
{
  "status": "healthy",
  "timestamp": "2025-...",
  "version": "3.0.0",
  "environment": "vercel"
}
```

### 浏览器访问测试
1. 打开部署后的URL
2. 应该能看到 "Data Forge · 车险变动成本实验室" 页面
3. 尝试上传一个小Excel文件测试

---

## 🆘 常见问题解决

### 问题1：git push 失败
```bash
# 如果推送失败，尝试强制推送
git push -f origin main
```

### 问题2：Vercel部署失败
1. 检查GitHub仓库是否公开
2. 确认requirements.txt文件存在
3. 查看Vercel部署日志
4. 重新触发部署

### 问题3：应用无法访问
1. 检查URL是否正确
2. 确认部署状态为"Ready"
3. 查看函数日志排查错误
4. 测试健康检查端点

---

## 🎉 部署成功后的下一步

### 立即测试
1. 准备一个小Excel文件（< 1MB）
2. 上传测试文件处理
3. 验证CSV输出结果

### 分享您的应用
获得部署URL后，您可以：
- 分享给同事使用
- 添加到书签方便访问
- 设置自定义域名（可选）

### 监控和维护
- 定期查看Vercel仪表板
- 监控使用情况和性能
- 及时更新代码（如有需要）

---

## 📞 需要帮助？

### 立即支持
- 📧 留言说明具体问题
- 🐛 提供错误信息和截图
- 📖 参考详细文档：VERCEL_DEPLOYMENT.md

### 自助排错
1. 确认每一步都按指南操作
2. 检查网络连接是否正常
3. 验证GitHub和Vercel账号权限
4. 查看相关日志信息

**🎯 选择您想要的部署方式，我们开始吧！**
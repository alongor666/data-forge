# 🚀 三分钟快速上手：克隆、运行与推送到 GitHub

## 1. 克隆或初始化项目
```bash
# 克隆已有仓库（示例）
git clone https://github.com/your-username/data-forge.git
cd data-forge

# 或在现有目录初始化
git init
```

## 2. 安装并运行（本地）
```bash
# 创建与激活虚拟环境（macOS/Linux）
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
# 访问 http://127.0.0.1:5000 或 http://127.0.0.1:5001（视配置而定）
```

## 3. 首次推送到 GitHub
```bash
# 在 GitHub 创建空仓库：https://github.com/your-username/data-forge.git

git add .
git commit -m "docs: 初始化并移除Vercel部署"
git branch -M main
git remote add origin https://github.com/your-username/data-forge.git
git push -u origin main
```

## 4. 后续推送到 GitHub
```bash
git add .
git commit -m "docs: 更新文档与说明"
git push

# 如需变更远程地址
git remote set-url origin https://github.com/your-username/data-forge.git
```

## 📋 使用须知

### 文件限制
- ✅ 单文件 ≤ 50MB
- ✅ 批量 ≤ 10个文件
- ✅ 格式：.xlsx/.xls

### 功能特性
- ✅ 27个标准字段自动映射
- ✅ 按年度智能拆分
- ✅ 实时上传验证
- ✅ 批量处理支持

## 🔧 自定义配置（可选）

### 环境变量示例（本地或自有服务器）
```
FLASK_ENV=production
MAX_FILE_SIZE=52428800  # 50MB
MAX_FILE_COUNT=10
```

## 🆘 遇到问题？

### 推送失败
1. 检查 Git 远程地址是否正确
2. 确认已在 GitHub 创建目标仓库
3. 查看 `git status` 与 `git log` 获取详细信息
4. 重试或更换网络环境

### 文件处理错误
1. 确认文件格式正确
2. 检查文件大小限制
3. 验证Excel文件完整性
4. 尝试小文件测试

## 📞 获取帮助

### 快速支持
- 📧 邮件：dataops@example.com
- 🐛 问题反馈：https://github.com/alongor/data-forge/issues
- 📖 完整文档：查看项目README文件

### 自助排查
1. 查看浏览器控制台错误信息
2. 检查文件是否符合要求
3. 尝试使用不同的Excel文件
4. 测试网络连接稳定性

## 🎯 下一步

### 探索高级功能
- 批量文件处理优化
- 自定义字段映射
- 数据质量检查
- 自动化工作流

### 集成到工作流
- 设置定期数据处理
- 集成到现有系统
- API接口调用
- 自定义输出格式

---

**🎊 恭喜！您现在拥有了一个功能完整的数据处理工具（无需 Vercel）！**

**💡 提示**：建议收藏部署后的URL，方便日常使用。
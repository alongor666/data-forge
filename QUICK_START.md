# 🚀 三分钟快速部署指南

## 一键部署到Vercel

### 步骤1：点击部署按钮
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/alongor/data-forge)

### 步骤2：GitHub授权
1. 点击按钮后会跳转到Vercel
2. 使用GitHub账号登录（或注册）
3. 授权Vercel访问您的GitHub仓库

### 步骤3：配置项目
1. 项目名称：`data-forge`（可自定义）
2. 环境变量：保持默认即可
3. 点击 "Deploy" 开始部署

### 步骤4：等待部署完成
- 部署过程大约需要2-3分钟
- 部署完成后会显示成功页面
- 点击 "Visit" 访问您的应用

## 🎉 部署成功！

### 访问您的应用
部署完成后，您会获得一个类似这样的URL：
```
https://data-forge-xxxxx.vercel.app
```

### 立即开始使用
1. 上传Excel文件（.xlsx/.xls格式）
2. 设置周序号（1-53）
3. 点击"开始处理"
4. 下载处理后的CSV文件

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

### 绑定自定义域名
1. 在Vercel Dashboard中选择项目
2. 进入 "Settings" → "Domains"
3. 添加您的域名
4. 配置DNS解析

### 环境变量配置
如需修改默认配置，在Vercel中添加环境变量：
```
FLASK_ENV=production
MAX_FILE_SIZE=52428800  # 50MB
MAX_FILE_COUNT=10
```

## 🆘 遇到问题？

### 部署失败
1. 检查GitHub仓库是否公开
2. 确认requirements.txt文件存在
3. 查看Vercel部署日志
4. 重新尝试部署

### 应用无法访问
1. 检查网络连接
2. 确认URL正确
3. 查看Vercel函数日志
4. 联系技术支持

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

**🎊 恭喜！您现在拥有了一个功能完整的数据处理工具！**

**💡 提示**：建议收藏部署后的URL，方便日常使用。
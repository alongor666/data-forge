# Data Forge - Vercel部署指南

## 🚀 快速部署到Vercel

本项目已经优化适配Vercel Serverless环境，支持完整的Excel文件处理功能。

### 一键部署
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/data-forge)

### 手动部署步骤

#### 1. 准备工作
- GitHub账号
- Vercel账号（可使用GitHub登录）
- 本项目代码

#### 2. 部署流程

**方式一：通过Vercel Dashboard**
1. 登录 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 导入GitHub仓库
4. 配置项目设置（见下方配置说明）
5. 点击 "Deploy"

**方式二：通过Vercel CLI**
```bash
# 安装Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

#### 3. 项目配置

**自动配置（推荐）**
项目已包含优化的 `vercel.json` 配置：
- Serverless函数最大执行时间：60秒
- 内存限制：50MB
- Python 3.9环境
- 自动临时目录管理

**环境变量**
```env
FLASK_ENV=production
PYTHON_VERSION=3.9
VERCEL_ENV=production
```

## 📋 部署要求

### 依赖包
- Flask >= 2.3.0
- pandas >= 1.5.0
- numpy >= 1.21.0
- openpyxl >= 3.0.0
- gunicorn >= 20.0.0

### 文件结构
```
data-forge/
├── app.py              # 主应用文件
├── vercel_app.py       # Vercel适配文件
├── vercel.json         # Vercel配置
├── requirements.txt    # 依赖包
├── templates/          # HTML模板
├── static/            # 静态文件
├── uploads/           # 上传文件（运行时创建）
└── 处理后/            # 输出文件（运行时创建）
```

## ⚙️ 技术优化

### Serverless适配
- **临时目录**：使用Vercel提供的系统临时目录
- **冷启动优化**：健康检查端点预热
- **内存管理**：优化大数据处理内存使用
- **超时处理**：60秒执行时间限制

### 性能配置
- 压缩响应数据
- 静态文件缓存
- 函数预热机制
- 错误重试策略

## 🔧 部署后配置

### 自定义域名
1. 在Vercel Dashboard中选择项目
2. 进入 "Settings" -> "Domains"
3. 添加自定义域名
4. 配置DNS解析

### 环境变量配置
在Vercel Dashboard中：
1. 选择项目 -> "Settings" -> "Environment Variables"
2. 添加所需的环境变量

### 性能监控
- 使用Vercel Analytics监控性能
- 配置日志查看错误信息
- 设置告警通知

## 📊 使用限制

### Vercel免费层限制
- **执行时间**：60秒/请求
- **内存使用**：50MB/函数
- **带宽**：100GB/月
- **文件大小**：建议单文件 < 10MB

### 应用限制
- 单文件最大：50MB（Flask限制）
- 批量处理：最多10个文件
- 输出格式：CSV文件
- 处理字段：27个标准字段

## 🚨 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
- 确认所有依赖包在requirements.txt中
- 检查Python语法错误
- 查看Vercel部署日志
- 确认文件路径正确

### Q: 文件处理超时？
A: 解决方案：
- 减少同时处理的文件数量
- 减小Excel文件大小
- 优化数据处理逻辑
- 考虑分批处理

### Q: 内存不足错误？
A: 优化建议：
- 处理较小的文件
- 减少并发处理
- 优化数据类型使用
- 及时清理临时文件

### Q: 如何查看日志？
A: 在Vercel Dashboard：
- 进入项目 -> "Logs" 标签
- 查看实时日志
- 筛选错误信息
- 下载日志文件

## 🔍 调试技巧

### 本地测试
```bash
# 模拟Vercel环境
export FLASK_ENV=production
export VERCEL_ENV=production
python vercel_app.py
```

### 健康检查
```bash
curl https://your-app.vercel.app/health
```

### 性能测试
```bash
# 测试文件上传
curl -X POST -F "file=@test.xlsx" https://your-app.vercel.app/upload
```

## 📈 监控和优化

### 关键指标
- 响应时间：< 30秒
- 成功率：> 95%
- 内存使用：< 40MB
- 冷启动时间：< 5秒

### 优化建议
1. **文件大小**：建议用户上传 < 5MB 的文件
2. **批量处理**：限制同时处理的文件数量
3. **缓存策略**：对静态资源启用缓存
4. **错误处理**：完善的错误提示和重试机制

## 🔗 相关链接

- [Vercel文档](https://vercel.com/docs)
- [Flask部署指南](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [项目GitHub仓库](https://github.com/your-username/data-forge)

## 📞 技术支持

如遇到部署问题，请：
1. 查看Vercel部署日志
2. 检查本指南的故障排除部分
3. 在GitHub Issues中提交问题
4. 联系技术支持

---

**部署状态**: ✅ 已优化适配Vercel
**最后更新**: 2025年1月
**版本**: v3.0.0
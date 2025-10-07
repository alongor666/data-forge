# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

使用中文沟通。
功能的具体变化同步在prd.md对应章节更新、说明。

## 项目概述

这是一个专注于车险变动成本明细分析的数据预处理Web应用，基于Flask构建，支持云端部署(Vercel/Heroku)。应用提供文件上传、数据处理和结果下载功能。

## 技术栈

- **后端**: Python 3.9+ / Flask
- **前端**: HTML5 / CSS3 / Vanilla JavaScript
- **部署**: Vercel (主要) / Heroku
- **数据处理**: pandas, openpyxl
- **样式**: Apple Keynote 风格深色主题

## 核心架构

### 应用结构
```
├── app.py                 # Flask应用主文件，包含所有路由和业务逻辑
├── templates/
│   ├── index.html         # 主页模板
│   └── upload.html        # 上传页面模板
├── static/
│   └── styles.css         # Apple Keynote风格样式
├── requirements.txt       # Python依赖
├── vercel.json           # Vercel部署配置
├── Procfile              # Heroku部署配置
└── 开发记录.md            # 详细的开发历程记录
```

### 关键设计模式

1. **云端适配策略**: 使用动态模块加载和模拟处理器确保云端兼容性
2. **无状态设计**: 使用临时目录(/tmp)，适配serverless环境
3. **错误处理**: 完善的异常捕获和用户友好的错误信息

## 常用命令

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器 (默认端口5000)
python app.py

# 启动测试服务器 (指定端口)
PORT=8080 python app.py

# 创建测试环境
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate
```

### 部署相关
```bash
# Vercel部署 (自动触发)
git push origin main

# Heroku部署
heroku create your-app-name
git push heroku main

# 测试上传功能 (本地)
curl -X POST -F "files=@test_data.csv" http://localhost:5000/upload

# 测试下载功能 (本地)
curl -X POST http://localhost:5000/download -o test_download.zip
```

## 核心功能实现

### 数据处理流程
1. **Excel转CSV**: `convert_excel_to_csv()` - 将上传的Excel文件转换为CSV格式
2. **数据预处理**: `CarInsuranceDataRestructurer.process_all_files()` - 执行数据清洗和重构
3. **元数据更新**: `DataStructureManager.update_metadata()` - 生成处理报告和元数据

### 关键路由
- `/` - 主页，显示应用介绍
- `/upload` - 文件上传页面和处理端点
- `/download` - 打包下载处理结果
- `/debug` - 调试信息接口

### 云端模拟模块
应用使用 `create_mock_preprocessor()` 创建兼容云端的数据处理模块，确保在无法加载外部依赖时仍能正常运行。

## 环境变量配置

- `PORT`: 应用端口 (默认: 5000)
- `HOST`: 绑定地址 (默认: 0.0.0.0)
- `DEBUG`: 调试模式 (默认: False)
- `DATA_PREPROCESSOR_SECRET`: Flask密钥

## 开发注意事项

### 文件路径处理
- 所有文件操作使用 `pathlib.Path` 进行路径处理
- 云端环境使用 `/tmp` 目录作为临时存储
- 确保在模拟模块中正确导入 `from pathlib import Path`

### 错误处理
- 所有API端点都有完善的异常捕获
- 返回统一的JSON响应格式
- 用户友好的错误信息显示

### 性能考虑
- 使用流式处理避免内存溢出
- 临时文件自动清理机制
- 适合处理中小型数据文件(几MB级别)

## 测试验证

### 功能测试checklist
- [ ] 服务器启动正常
- [ ] 主页路由响应正常
- [ ] 上传页面加载正常
- [ ] 文件上传处理成功
- [ ] 数据处理完成
- [ ] 下载功能正常
- [ ] ZIP文件内容正确

### 部署验证
确保以下文件在生产环境中可正常访问:
- `data_restructure_report.json` - 处理报告
- `metadata.json` - 元数据信息
- `processed_*.csv` - 处理后的数据文件

## 故障排除

### 常见问题
1. **上传错误**: 检查 `load_preprocessor_module()` 是否正确使用模拟模块
2. **路径错误**: 确保所有Path对象正确初始化
3. **部署失败**: 检查 `vercel.json` 配置和依赖项是否完整

### 调试工具
- 使用 `/debug` 端点获取系统状态信息
- 检查服务器日志文件
- 本地测试环境验证功能完整性

## 项目历史

详细的开发过程和问题解决方案记录在 `开发记录.md` 中，包括:
- 云端适配过程
- 错误修复历程
- 性能优化记录
- 部署配置演进

参考最新提交记录了解最近的功能更新和bug修复。
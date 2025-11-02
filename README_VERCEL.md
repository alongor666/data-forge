# 🚀 Data Forge - Vercel在线版本

## 📋 项目简介

Data Forge 是一个专业的车险变动成本数据处理工具，专为保险行业设计，提供智能的Excel到CSV转换服务。

### ✨ 核心功能
- **智能字段映射**：自动识别27个标准字段
- **批量文件处理**：支持同时处理多个Excel文件
- **年度自动拆分**：按保单年度智能分组输出
- **数据质量保障**：严格遵循处理规范，确保数据准确性
- **实时上传验证**：文件大小、格式、数量实时检查

### 🎯 适用场景
- 车险变动成本分析报告
- 保单数据标准化处理
- 业务数据质量检查
- 年度数据归档整理

## 🚀 快速开始

### 一键部署到Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/alongor/data-forge)

### 使用在线演示
[访问在线演示](https://data-forge.vercel.app)（如果已部署）

## 📊 使用限制

### 文件限制
- **单文件大小**：≤ 50MB
- **批量文件数**：≤ 10个文件
- **支持格式**：.xlsx, .xls
- **处理字段**：27个标准字段

### Vercel免费层限制
- **每月带宽**：100GB
- **执行时间**：60秒/请求
- **内存限制**：50MB/函数

## 🛠️ 本地开发

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/alongor/data-forge.git
cd data-forge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

### 访问应用
打开浏览器访问：http://localhost:5001

## 📁 文件结构

```
data-forge/
├── app.py                  # 主应用文件
├── vercel_app.py          # Vercel适配文件
├── vercel.json            # Vercel配置
├── requirements.txt       # Python依赖
├── templates/             # HTML模板
│   └── index.html        # 主页面
├── static/               # 静态资源
│   └── styles.css        # 样式文件
├── uploads/              # 上传文件（运行时创建）
├── 处理后/               # 输出文件（运行时创建）
└── docs/                 # 文档
```

## 🔧 部署配置

### Vercel部署
项目已优化适配Vercel Serverless环境：
- ✅ 自动临时目录管理
- ✅ Serverless函数优化
- ✅ 内存使用优化
- ✅ 冷启动性能优化

### 环境变量
```env
FLASK_ENV=production
PYTHON_VERSION=3.9
VERCEL_ENV=production
```

## 📈 性能优化

### 前端优化
- 文件上传实时验证
- 批量错误处理
- 大文件确认对话框
- 实时文件统计信息

### 后端优化
- 内存高效的数据处理
- 临时文件自动清理
- 错误重试机制
- 健康检查端点

## 🎯 使用流程

### 1. 文件上传
- 拖拽或点击选择Excel文件
- 系统自动验证文件格式和大小
- 为每个文件设置周序号

### 2. 数据处理
- 点击"开始处理"按钮
- 实时显示处理进度
- 自动按年度拆分数据

### 3. 结果下载
- 处理完成后显示结果
- 支持单个CSV文件下载
- 支持ZIP打包批量下载

## 🔍 字段说明

### 筛选维度字段（18个）
- 刷新时间、保险起期、业务类型
- 成都中支、二级机构、三级机构
- 客户类别、险种类、新能源标识
- 交三/主全、过户标识、续保情况
- 车险等级、高速风险等级、货车评分
- 终端来源、周次

### 绝对值字段（9个）
- 签单保费、满期保费、保单件数
- 赔案件数、已报告赔款、费用金额
- 商业险折前保费、保费计划、边际贡献额

## 🚨 常见问题

### Q: 文件处理失败怎么办？
A: 检查以下几点：
- 文件格式是否为.xlsx或.xls
- 文件大小是否超过50MB
- 网络连接是否稳定
- 文件是否被其他程序占用

### Q: 处理时间过长？
A: 建议优化：
- 减少同时处理的文件数量
- 减小Excel文件大小
- 确保网络连接稳定

### Q: 输出字段不完整？
A: 可能原因：
- 输入文件缺少必要字段
- 字段名称不匹配标准模板
- 数据格式不规范

## 📞 技术支持

### 获取帮助
- 📧 邮箱支持：dataops@example.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/alongor/data-forge/issues)
- 📖 完整文档：[项目Wiki](https://github.com/alongor/data-forge/wiki)

### 更新日志
查看 [CHANGELOG.md](CHANGELOG.md) 了解最新更新

## 🤝 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发规范
- 遵循PEP 8 Python编码规范
- 添加适当的注释和文档
- 编写测试用例
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢保险行业的专业需求反馈
- 感谢开源社区的贡献和支持
- 感谢Vercel提供优秀的部署平台

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**

**🔗 项目地址**: https://github.com/alongor/data-forge
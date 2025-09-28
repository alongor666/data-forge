# Data Forge - 数据锻造工坊

> 🔥 一个现代化的数据预处理与分析Web应用，专注于车险变动成本明细分析

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/alongor666/data-forge)

## ✨ 功能特性

- 🎯 **一键预处理**：批量 Excel→CSV 转换 + 数据清洗
- 📊 **智能分析**：字段标准化、绝对值计算、按年度拆分
- 🎨 **现代UI**：Apple Keynote 风格深色主题
- 📱 **响应式设计**：支持桌面和移动设备
- 📦 **结果下载**：自动打包处理结果为ZIP文件
- 🌐 **在线部署**：支持Vercel、Heroku等平台一键部署

## 🌐 在线体验

🔗 [访问在线演示](https://data-forge.vercel.app)

## 🚀 快速开始

### 在线部署（推荐）

#### 方法1: Vercel 一键部署
点击上方的 "Deploy to Vercel" 按钮，或访问：
```
https://vercel.com/new/clone?repository-url=https://github.com/alongor666/data-forge
```

#### 方法2: 手动部署到Vercel
1. Fork 此仓库到你的GitHub账号
2. 在 [Vercel](https://vercel.com) 创建新项目
3. 导入你fork的仓库
4. Vercel会自动检测Python项目并部署

#### 方法3: Heroku部署
```bash
# 安装Heroku CLI后执行
git clone https://github.com/alongor666/data-forge.git
cd data-forge
heroku create your-app-name
git push heroku main
```

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/alongor666/data-forge.git
cd data-forge

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 打开浏览器访问 http://localhost:5000
```

## 📖 使用说明

1. **设置目录路径**
   - 源Excel目录：存放原始.xlsx文件的目录
   - 转换CSV目录：存放转换后.csv文件的目录
   - 输出目录：处理结果的输出目录

2. **扫描数据文件**
   - 点击"扫描目录"查看可用的数据文件

3. **执行数据预处理**
   - 点击"一键预处理"开始处理
   - 系统会显示处理进度和结果统计

4. **下载处理结果**
   - 处理完成后可打包下载所有结果文件

## 🛠️ 技术栈

- **后端**: Python 3.9+ / Flask
- **前端**: HTML5 / CSS3 / Vanilla JavaScript
- **部署**: Vercel / Heroku / Docker
- **样式**: Apple Keynote 风格深色主题

## 📁 项目结构

```
data-forge/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── Procfile              # Heroku部署配置
├── vercel.json           # Vercel部署配置
├── templates/
│   └── index.html        # 主页模板
├── static/
│   └── styles.css        # 样式文件
└── README.md             # 项目说明
```

## 🔧 环境变量配置

可通过环境变量自定义运行参数：

- `PORT`: 应用端口 (默认: 5000)
- `HOST`: 绑定地址 (默认: 0.0.0.0)
- `DEBUG`: 调试模式 (默认: False)
- `DATA_PREPROCESSOR_SECRET`: Flask密钥

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 此仓库
2. 创建feature分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## ❓ 常见问题

**Q: 如何处理大型数据文件？**
A: 系统支持批量处理，大文件会自动分块处理以避免内存溢出。

**Q: 支持哪些数据格式？**
A: 目前支持Excel (.xlsx) 和 CSV 格式，未来会支持更多格式。

**Q: 如何自定义数据处理逻辑？**
A: 可以修改 `app.py` 中的数据处理函数来适应不同的业务需求。

---

<div align="center">
  <strong>🔥 Data Forge - 数据锻造，精准高效 🔥</strong>
</div>

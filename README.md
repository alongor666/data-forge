# Data Forge - 数据锻造工坊

🔥 一个现代化的数据预处理与分析Web应用，专注于车险变动成本明细分析

## ✨ 功能特性

- 🎯 **一键预处理**: 支持Excel到CSV的转换和数据清洗。
- 📊 **智能分析**: 自动进行字段标准化、绝对值计算，并按年度拆分数据。
- 🎨 **现代UI**: 采用Apple Keynote风格的深色主题，界面简洁优雅。
- 📱 **响应式设计**: 完美适配桌面和移动设备。
- 📦 **结果下载**: 处理完成的数据会自动打包为ZIP文件，方便一键下载。
- 🌐 **在线部署**: 支持Vercel、Heroku等平台一键部署。

## 🚀 快速开始

### 本地运行

1.  **克隆仓库**
    ```bash
    git clone https://github.com/alongor666/data-forge.git
    cd data-forge
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **启动应用**
    ```bash
    python app.py
    ```

4.  **访问应用**
    在浏览器中打开 `http://localhost:5000`

## 📖 使用说明

1.  **上传文件**: 点击“选择文件”按钮，上传您的Excel数据文件。
2.  **数据处理**: 上传后，系统会自动进行数据预处理。
3.  **下载结果**: 处理完成后，页面会提供一个ZIP压缩包的下载链接，其中包含所有处理好的CSV文件。

## 🛠️ 技术栈

-   **后端**: Python 3.9+ / Flask
-   **前端**: HTML5 / CSS3 / Vanilla JavaScript
-   **部署**: Vercel / Heroku / Docker

## 📁 项目结构

```
data-forge/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── Procfile               # Heroku部署配置
├── vercel.json            # Vercel部署配置
├── templates/
│   └── index.html         # 主页模板
├── static/
│   └── styles.css         # 样式文件
└── README.md              # 项目说明
```

## 🔧 环境变量配置

可通过环境变量自定义运行参数：

-   `PORT`: 应用端口 (默认: 5000)
-   `HOST`: 绑定地址 (默认: 0.0.0.0)
-   `DEBUG`: 调试模式 (默认: False)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1.  Fork 此仓库
2.  创建feature分支 (`git checkout -b feature/AmazingFeature`)
3.  提交更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  创建Pull Request

## 📄 许可证

[MIT License](LICENSE)

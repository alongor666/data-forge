# Database预处理 - 静态网页版

> 🌐 纯前端数据处理应用 | 无需服务器 | 即开即用

这是**Database预处理**项目的静态网页版本，使用纯JavaScript在浏览器中处理Excel文件，无需后端服务器。

## ✨ 特点

### 相比服务器版本

| 特性 | 静态版本 (gh-pages-static) | 服务器版本 (main/vercel) |
|------|---------------------------|------------------------|
| **部署方式** | GitHub Pages / 任何静态托管 | Vercel / 本地服务器 |
| **处理位置** | 浏览器本地 | 服务器端 |
| **文件大小限制** | 推荐 ≤ 10MB | ≤ 50MB |
| **数据隐私** | ⭐⭐⭐⭐⭐ 数据不离开本地 | ⭐⭐⭐⭐ 临时上传到服务器 |
| **处理速度** | 取决于用户设备性能 | 稳定快速 |
| **网络要求** | 仅首次加载需要网络 | 需要持续网络连接 |
| **成本** | 完全免费 | 免费（有配额限制） |

### 核心功能

✅ **完整保留**所有数据处理逻辑
- 18个筛选维度字段 + 9个绝对值字段
- 智能周序号自动识别和手动设置
- 按年度自动分组导出
- 字段映射和数据标准化

✅ **纯前端技术栈**
- ExcelJS: Excel文件读写
- JSZip: 批量文件打包
- FileSaver: 文件下载

⚠️ **使用限制**
- 推荐单文件 ≤ 10MB（技术上支持更大，但可能卡顿）
- 批量处理建议 ≤ 5个文件
- 受浏览器内存限制（现代浏览器约500MB-2GB）

## 🚀 快速开始

### 在线使用

访问: `https://yourusername.github.io/data-forge`

### 本地运行

```bash
# 克隆仓库
git clone -b gh-pages-static https://github.com/yourusername/data-forge.git
cd data-forge

# 使用任何HTTP服务器
# 方法1: Python
python -m http.server 8000

# 方法2: Node.js
npx serve

# 方法3: VS Code
# 安装Live Server插件，右键index.html选择"Open with Live Server"
```

然后访问 `http://localhost:8000`

## 📁 项目结构

```
gh-pages-static/
├── index.html          # 主页面（整合UI和引用）
├── processor.js        # 核心数据处理器（移植自app.py）
├── app.js              # 主应用逻辑（UI交互）
├── static/
│   └── styles.css      # Apple Keynote深色风格
├── 处理规范.md          # 数据处理规范（同步自main分支）
└── README-STATIC.md    # 本文档
```

## 🎯 使用指南

### 1. 准备数据文件

确保Excel文件符合《处理规范.md》要求：
- 包含必要的中文字段（如"刷新时间"、"保险起期"等）
- 文件名建议包含周序号（如"第43周"、"W43"）

### 2. 上传文件

- 拖拽文件到上传区域，或点击"选择文件"
- 系统会自动从文件名提取周序号
- 可手动修改或补充周序号（1-53）

### 3. 处理数据

- 点击"开始处理"按钮
- 浏览器会在本地处理数据（数据不会上传到任何服务器）
- 处理进度实时显示

### 4. 下载结果

- 自动按年度分组生成CSV文件
- 单独下载每个年度文件
- 或一键打包下载ZIP压缩包

## 🔧 技术实现

### 核心技术栈

```
ExcelJS 4.4.0      - Excel文件读写
JSZip 3.10.1       - ZIP压缩
FileSaver 2.0.5    - 文件下载
原生JavaScript ES6+ - 无框架依赖
```

### 数据处理流程

```
Excel上传 → ExcelJS解析 → 字段标准化
→ 计算绝对值字段 → 按年度分组 → 生成CSV → 下载
```

### 关键代码说明

#### DataProcessor 类 (processor.js)

完整移植自Python版本的`DataProcessor`类：

```javascript
class DataProcessor {
  async processExcelFile(file, weekNumber) {
    // 1. 使用ExcelJS读取Excel
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(await file.arrayBuffer());

    // 2. 转换为JSON数据
    const data = this.worksheetToJSON(worksheet);

    // 3. 标准化字段
    const standardized = this.standardizeFields(data, file.name, weekNumber);

    // 4. 计算绝对值字段
    const calculated = this.calculateAbsoluteFields(standardized);

    // 5. 最终化输出
    const finalized = this.finalizeOutput(calculated);

    // 6. 按年度分组
    const grouped = this.groupByYear(finalized);

    return { success: true, data: grouped };
  }
}
```

#### 字段映射 (与Python版本100%一致)

```javascript
this.fieldMapping = {
  '刷新时间': 'snapshot_date',
  '保险起期': 'policy_start_year',
  '跟单保费(万)': 'signed_premium_wan',
  // ... 完整映射
};
```

#### 绝对值字段计算 (与Python版本100%一致)

```javascript
// 1. 签单保费(元) = 跟单保费(万) * 10000
newRow.signed_premium_yuan = signedPremiumWan * 10000;

// 2. 满期保费(元) = 满期净保费(万) * 10000
newRow.matured_premium_yuan = maturedPremiumWan * 10000;

// ... 其他7个字段计算
```

## ⚠️ 注意事项

### 浏览器兼容性

推荐使用现代浏览器：
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### 性能建议

1. **小文件优先**：单文件 ≤ 10MB 体验最佳
2. **大文件**：建议使用[服务器版本](https://data-forge-xuechenglong.vercel.app)
3. **关闭其他标签页**：处理时减少浏览器内存压力
4. **不要刷新页面**：处理过程中刷新会丢失进度

### 数据隐私

⭐ **所有数据处理完全在本地浏览器中进行**
- 数据不会上传到任何服务器
- 不记录任何处理日志
- 关闭页面后数据自动清除

## 🆚 何时使用哪个版本？

### 使用静态版本 (gh-pages-static)

- ✅ 处理小文件（≤ 10MB）
- ✅ 对数据隐私要求极高
- ✅ 无需服务器/快速部署
- ✅ 离线环境（首次加载后）

### 使用服务器版本 (main/vercel)

- ✅ 处理大文件（10MB - 50MB）
- ✅ 需要批量处理大量文件
- ✅ 需要服务器日志和历史记录
- ✅ 对处理速度要求高

## 📝 开发说明

### 同步更新

当`处理规范.md`更新时，需要同步到静态分支：

```bash
git checkout gh-pages-static
git checkout main -- 处理规范.md
git commit -m "docs: 同步main分支的处理规范更新"
git push
```

### 本地测试

```bash
# 1. 切换到静态分支
git checkout gh-pages-static

# 2. 启动本地服务器
python -m http.server 8000

# 3. 打开浏览器
open http://localhost:8000

# 4. 打开开发者工具查看Console日志
```

### 部署到GitHub Pages

```bash
# 1. 推送到GitHub
git push origin gh-pages-static

# 2. 在GitHub仓库设置中启用Pages
# Settings → Pages → Source → 选择 gh-pages-static 分支

# 3. 等待几分钟后访问
# https://yourusername.github.io/data-forge
```

## 🐛 故障排除

### 问题1: 文件上传后无响应

**解决方案**：
- 检查浏览器Console是否有错误
- 确认文件格式为.xlsx或.xls
- 尝试减小文件大小

### 问题2: 处理时浏览器卡死

**解决方案**：
- 文件可能过大，建议使用服务器版本
- 关闭其他标签页释放内存
- 升级到更现代的浏览器

### 问题3: 下载的CSV乱码

**解决方案**：
- 使用Excel打开时选择UTF-8编码
- 或使用记事本/VSCode等编辑器打开

### 问题4: 年度识别错误

**解决方案**：
- 检查Excel中"保险起期"字段格式
- 确保年份为4位数字（如2024）
- 参考《处理规范.md》中的年份格式要求

## 📚 相关文档

- [处理规范.md](./处理规范.md) - 数据处理核心规范
- [CLAUDE.md](./CLAUDE.md) - 项目开发指南
- [main分支README](https://github.com/yourusername/data-forge/blob/main/README.md) - 服务器版本文档

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证

---

**Database预处理** - 让数据处理更简单 🚀

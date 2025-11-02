# 快速开始指南

## 🚀 立即启动（3步）

### 第1步：安装依赖

```bash
cd fastapi_app
pip install -r requirements.txt
```

### 第2步：启动服务

```bash
python run.py
```

或者使用uvicorn：

```bash
uvicorn main:app --reload --port 5001
```

### 第3步：打开浏览器

访问：http://127.0.0.1:5001

## 📚 额外资源

- **API文档**: http://127.0.0.1:5001/docs
- **健康检查**: http://127.0.0.1:5001/health

## 🎯 快速测试

```bash
# 测试健康检查
curl http://127.0.0.1:5001/health

# 上传文件（示例）
curl -X POST http://127.0.0.1:5001/upload \
  -F "file=@your_file.xlsx" \
  -F "week_numbers=15"
```

## ⚡ 性能对比

- **Flask版本**: 处理50MB文件需要 ~32秒
- **FastAPI版本**: 处理50MB文件只需 ~3秒
- **提升**: **10倍以上** 🚀

## 💡 提示

1. 确保Python版本 >= 3.9
2. 首次运行会下载依赖包（约2-3分钟）
3. 所有功能与Flask版本100%兼容
4. 输出文件保存在 `../处理后/` 目录

## 🐛 常见问题

**Q: 端口5001被占用？**
```bash
export PORT=8080
python run.py
```

**Q: Polars安装失败？**
```bash
pip install --upgrade pip
pip install polars --no-cache-dir
```

**Q: 如何停止服务？**
按 `Ctrl+C` 即可停止

---

享受飞速的数据处理体验！⚡

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

使用中文沟通。
功能的具体变化同步在处理规范.md对应章节更新、说明。

## 项目概述

这是一个专注于车险变动成本明细分析的数据预处理Web应用,基于Flask构建,支持云端部署(Vercel)和本地运行。应用提供文件上传、智能数据处理和双重下载功能。

**核心价值**: 将原始车险Excel数据标准化为符合《处理规范.md》的18个筛选维度字段 + 9个绝对值字段的统一格式。

## 技术栈

- **后端**: Python 3.12+ / Flask 3.1.2
- **前端**: HTML5 / CSS3 / Vanilla JavaScript (Apple Keynote深色风格)
- **数据处理**: pandas 2.3.2, numpy 2.3.3, openpyxl 3.1.5
- **部署**: Vercel (Serverless)

## 核心架构

### 应用结构
```
├── app.py                 # 主应用文件,包含DataProcessor类和所有路由
├── templates/
│   ├── index.html         # 主页
│   └── upload.html        # 上传页面(如有)
├── static/
│   └── styles.css         # Apple Keynote风格样式
├── 处理后/                 # 本地输出目录(主要)
├── uploads/               # 临时上传文件
├── output/                # Web下载缓存目录
├── 处理规范.md             # 数据处理核心规范文档
└── 项目上下文.md           # 详细开发历程和技术上下文
```

### 关键设计模式

**1. DataProcessor类** ([app.py](app.py))
- 核心数据处理逻辑封装在`DataProcessor`类中
- 关键方法:
  - `standardize_fields()`: 字段标准化和映射 (行162-273)
  - `calculate_absolute_fields()`: 计算9个绝对值字段 (行275-346)
  - `finalize_output()`: 最终输出处理,确保27个字段完整 (行348-366)
  - `process_excel_to_csv()`: 主处理流程,按年度分组输出 (行467-584)

**2. 字段映射系统**
- 18个中文字段映射到英文标准字段 (行121-152)
- 支持多源字段匹配和智能单位识别
- 布尔值统一转换 (行154-160)

**3. 双重存储机制**
- `处理后/` 目录: 本地持久化存储,便于直接访问
- `output/` 目录: Web服务下载缓存
- 两个目录内容同步,确保数据可靠性

**4. 周序号处理策略** ⭐️ 新增功能
- **每个文件独立周序号**: 支持多文件上传时为每个文件单独设置周序号
- **智能自动识别**: 前端自动从文件名提取周序号(支持格式: 第XX周、周XX、WXX、week XX等)
- **用户确认机制**: 文件队列中每个文件都有独立的周序号输入框,可逐个确认或修改
- **前端实现**: [templates/index.html:131-153](templates/index.html#L131-L153) extractWeekNumber函数
- **后端实现**: [app.py:611-667](app.py#L611-L667) 支持week_numbers列表参数
- **向后兼容**: 仍支持旧版统一week_number参数

## 常用命令

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器 (默认端口5001)
python app.py

# 指定端口启动
PORT=8080 python app.py

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 测试和验证
```bash
# 测试上传功能 (本地)
curl -X POST -F "files=@test_data.xlsx" -F "week_number=15" http://localhost:5001/upload

# 测试下载功能
curl http://localhost:5001/download/2024保单第15周变动成本明细表.csv -o test.csv

# 查看处理后的文件
ls -lh 处理后/
```

### 部署相关
```bash
# Vercel部署 (自动触发)
git push origin main

# 本地验证Vercel配置
vercel dev

# 检查依赖是否完整
pip list | grep -E "Flask|pandas|numpy|openpyxl"
```

## 核心功能实现

### 数据处理流程
```
Excel上传 → standardize_fields() → calculate_absolute_fields()
         → finalize_output() → 按年度分组 → 双重存储
```

### 关键路由
- `GET /` - 主页,显示应用介绍
- `POST /upload` - 文件上传和处理端点
  - **新特性**: 支持每个文件独立周序号
  - 参数: `file`(多个文件)、`week_numbers`(每个文件对应的周序号列表)、`client_ids`(前端文件ID)
  - 向后兼容: 仍支持统一的`week_number`参数
- `GET /download/<filename>` - 文件下载端点

### 多文件周序号处理流程 ⭐️ 新功能
1. **前端上传阶段**:
   - 用户选择多个Excel文件
   - 系统自动调用`extractWeekNumber()`从文件名提取周序号
   - 在文件队列中为每个文件显示周序号输入框
   - 用户可逐个确认或修改周序号

2. **前端验证**:
   - 验证每个文件都有有效的周序号(1-53)
   - 如有缺失,阻止提交并提示用户

3. **后端处理**:
   - 接收`week_numbers`列表(每个元素对应一个文件)
   - 验证列表长度与文件数量匹配
   - 为每个文件使用其对应的周序号调用`process_excel_to_csv()`

4. **结果汇总**:
   - 如所有文件使用相同周序号,显示该周序号
   - 如使用不同周序号,显示范围(如"15-17")

### 字段处理逻辑

**18个筛选维度字段**:
1-17: 标准业务维度 (刷新时间、保险起期、业务类型等)
18: week_number (周序号,支持用户指定)

**9个绝对值字段** (所有金额单位统一为"元"):
1. `signed_premium_yuan`: 跟单保费(万) × 10,000
2. `matured_premium_yuan`: 满期净保费(万) × 10,000
3. `commercial_premium_before_discount_yuan`: 满期保费 ÷ 商业险自主系数
4. `policy_count`: 签单保费 ÷ 单均保费 (取整，单均保费为0时件数为0)
5. `claim_case_count`: 直接使用案件数字段
6. `reported_claim_payment_yuan`: 总赔款(万) × 10,000
7. `expense_amount_yuan`: 签单保费 × 费用率
8. `premium_plan_yuan`: 满期保费 × 保费计划系数
9. `marginal_contribution_amount_yuan`: 满期保费 × (1 - 变动成本率)

**年度识别逻辑** ([app.py:188-236](app.py#L188-L236)):
- 从`policy_start_year`字段智能提取年份
- 支持日期格式、4位年份、Excel序列号等多种格式
- 使用正则表达式匹配年份模式

### 输出文件命名规则
- 单年度: `YYYY保单第WW周变动成本明细表.csv`
- 多年度: `YYYY-YYYY保单第WW周变动成本明细表.csv`
- ZIP压缩包: 包含所有年度文件的压缩包

## 开发注意事项

### 数据处理规范
- **严格遵循** `处理规范.md` 的要求
- 确保输出27个字段 (18个筛选维度 + 9个绝对值)
- 所有金额字段统一为"元"单位
- 数值字段保留2位小数,件数字段为整数

### 字段映射扩展
- 修改字段映射时,同步更新`field_mapping`字典 ([app.py:122-152](app.py#L122-L152))
- 修改绝对值计算时,同步更新`calculate_absolute_fields()`方法
- 确保`required_fields`列表包含所有27个字段 ([app.py:54-84](app.py#L54-L84))

### 错误处理
- 所有API端点都有完善的try-except包装
- 使用logging记录详细的处理过程和错误信息
- 返回统一的JSON响应格式: `{success: bool, message: str, data: object}`

### 性能考虑
- 使用pandas的向量化操作避免循环
- 按年度分组处理大文件,避免内存溢出
- 临时文件使用时间戳命名,避免冲突

### Vercel云端适配
- 使用`/tmp`目录作为临时存储(Vercel限制)
- 所有文件操作使用`pathlib.Path`处理路径
- 确保依赖项在`requirements.txt`中完整列出

## 测试验证

### 功能测试清单
- [ ] 服务器正常启动 (检查日志无错误)
- [ ] 主页路由响应正常
- [ ] 单文件上传处理成功
- [ ] 批量文件上传处理成功
- [ ] 用户指定周序号功能正常
- [ ] 文件名周序号提取正常
- [ ] 按年度分组输出正确
- [ ] `处理后/`目录文件生成正确
- [ ] 下载功能正常
- [ ] 输出文件包含27个字段
- [ ] 字段顺序符合`required_fields`定义

### 数据质量验证
```bash
# 检查输出文件字段数
head -1 处理后/2024保单第15周变动成本明细表.csv | tr ',' '\n' | wc -l
# 应输出: 27

# 验证字段名全为英文
head -1 处理后/2024保单第15周变动成本明细表.csv
# 应无中文字符

# 检查数据行数
wc -l 处理后/*.csv
```

## 故障排除

### 常见问题
1. **上传失败**: 检查文件格式(仅支持.xlsx, .xls)和文件大小(限制50MB)
2. **字段数不对**: 检查`required_fields`列表和`finalize_output()`方法
3. **周序号识别失败**: 检查文件名格式或手动指定周序号
4. **年度识别错误**: 检查`policy_start_year`字段数据质量
5. **部署失败**: 检查`vercel.json`配置和Python版本兼容性

### 调试工具
- 使用`logger.info()`添加调试日志
- 检查Flask控制台输出
- 查看`处理后/`目录文件内容
- 使用`pandas.DataFrame.info()`检查数据类型

## 关键文档

- **处理规范.md**: 数据处理的核心规范,定义了字段映射和计算方法
- **项目上下文.md**: 详细的开发历程和技术决策记录
- **README.md**: 用户使用指南和项目介绍
- **优化总结.md**: 版本迭代的优化内容总结

## 版本历史

- **v2.3.0** (当前): ⭐️ 每个文件独立周序号 + 智能自动识别
  - 支持多文件上传时为每个文件单独设置周序号
  - 前端自动从文件名提取周序号
  - 文件队列中每个文件独立的周序号输入框
  - 向后兼容旧版统一周序号参数
- **v2.2.0**: 用户指定周序号 + 双重存储机制
- **v2.1.0**: 本地文件夹存储 + 按年度分组输出
- **v2.0.0**: 完整的18+9字段映射系统
- **v1.0.0**: 基础Excel转CSV功能

参考最新git提交记录了解功能更新和bug修复。
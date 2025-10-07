# CSV规范符合性检查报告

## 检查概要
- **检查文件**: `2024保单第40周变动成本明细表.csv`
- **检查时间**: 2024年第40周
- **总体符合性**: ❌ **不符合规范要求**

## 详细检查结果

### 1. 字段总数检查
- **规范要求**: 25个字段
- **实际情况**: 36个字段
- **符合性**: ❌ **不符合** (超出11个字段)

### 2. 字段顺序检查
- **规范要求**: 17个筛选维度字段 + 8个绝对值字段，按指定顺序排列
- **实际情况**: 字段顺序严重不符合规范
- **符合性**: ❌ **不符合** (发现20个字段不匹配)

#### 字段对比详情

##### 筛选维度字段（前17个位置）
| 位置 | 规范要求字段 | 实际字段 | 匹配状态 |
|------|-------------|----------|----------|
| 1 | snapshot_date | snapshot_date | ✓ |
| 2 | policy_start_year | policy_start_year | ✓ |
| 3 | business_type_category | business_type_category | ✓ |
| 4 | chengdu_branch | chengdu_branch | ✓ |
| 5 | third_level_organization | third_level_organization | ✓ |
| 6 | customer_category_3 | customer_category_3 | ✓ |
| 7 | insurance_type | insurance_type | ✓ |
| 8 | is_new_energy_vehicle | is_new_energy_vehicle | ✓ |
| 9 | coverage_type | coverage_type | ✓ |
| 10 | is_transferred_vehicle | is_transferred_vehicle | ✓ |
| 11 | renewal_status | renewal_status | ✓ |
| 12 | vehicle_insurance_grade | vehicle_insurance_grade | ✓ |
| 13 | highway_risk_grade | highway_risk_grade | ✓ |
| 14 | large_truck_score | large_truck_score | ✓ |
| 15 | small_truck_score | small_truck_score | ✓ |
| 16 | terminal_source | terminal_source | ✓ |
| 17 | week_number | field_11 | ❌ |

##### 绝对值字段（第18-25个位置）
| 位置 | 规范要求字段 | 实际字段 | 匹配状态 |
|------|-------------|----------|----------|
| 18 | signed_premium_yuan | field_9 | ❌ |
| 19 | matured_premium_yuan | field_12 | ❌ |
| 20 | policy_count | field_4 | ❌ |
| 21 | claim_case_count | field_6 | ❌ |
| 22 | reported_claim_payment_yuan | 案均赔款 | ❌ |
| 23 | expense_amount_yuan | field_5 | ❌ |
| 24 | commercial_premium_before_discount_yuan | 满期赔付率 | ❌ |
| 25 | marginal_contribution_amount_yuan | field_7 | ❌ |

##### 额外字段（第26-36个位置）
| 位置 | 实际字段 | 说明 |
|------|----------|------|
| 26 | 变动成本率 | 规范外字段 |
| 27 | 商业险自主系数 | 规范外字段 |
| 28 | signed_premium_yuan | 重复字段 |
| 29 | matured_premium_yuan | 重复字段 |
| 30 | policy_count | 重复字段 |
| 31 | claim_case_count | 重复字段 |
| 32 | reported_claim_payment_yuan | 重复字段 |
| 33 | expense_amount_yuan | 重复字段 |
| 34 | commercial_premium_before_discount_yuan | 重复字段 |
| 35 | marginal_contribution_amount_yuan | 重复字段 |
| 36 | week_number | 重复字段 |

### 3. 数据类型检查
- **总体情况**: 数据类型分布不符合规范要求
- **实际分布**: 
  - float64: 16个字段
  - object: 13个字段  
  - int64: 5个字段
  - bool: 2个字段

#### 关键问题
1. **字段重复**: 规范要求的8个绝对值字段在文件末尾重复出现
2. **字段命名**: 部分字段使用了临时命名（如field_4, field_5等）
3. **额外字段**: 包含了规范外的字段（变动成本率、商业险自主系数、案均赔款、满期赔付率）
4. **字段缺失**: week_number字段在第17位置缺失，出现在第36位置

## 问题分析

### 主要问题
1. **字段数量超标**: 实际36个字段 vs 规范25个字段
2. **字段顺序混乱**: 绝对值字段位置完全错误
3. **字段重复**: 8个核心绝对值字段重复出现
4. **命名不规范**: 使用临时字段名（field_X）

### 可能原因
1. 数据处理过程中字段映射错误
2. 多个数据源合并时字段重复
3. 字段重命名过程不完整
4. 缺少最终的字段筛选和排序步骤

## 建议修复方案

### 1. 立即修复
- 删除重复的绝对值字段（第28-36位置）
- 修正第17-25位置的字段名称和顺序
- 删除规范外的额外字段

### 2. 数据处理流程优化
- 在数据输出前增加字段验证步骤
- 实施严格的字段映射和重命名规则
- 添加字段顺序和数量的自动检查

### 3. 质量控制
- 建立CSV输出的标准化模板
- 实施输出前的自动化规范检查
- 增加数据质量监控机制

## 结论

当前输出的CSV文件**严重不符合**规范要求，主要表现在字段数量超标、顺序错误、存在重复字段等问题。建议立即修复数据处理流程，确保输出符合25字段的标准规范。
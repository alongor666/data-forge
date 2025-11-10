/**
 * 数据处理器 - JavaScript版本
 * 完整移植自 app.py 的 DataProcessor 类
 * 严格按照处理规范.md执行数据转换和字段映射
 */

class DataProcessor {
  constructor() {
    // 完整的27字段列表（严格按照输出模板.csv顺序）
    this.requiredFields = [
      // 18个筛选维度字段
      'snapshot_date',           // 刷新时间
      'policy_start_year',       // 保险起期
      'business_type_category',  // 业务类型
      'chengdu_branch',          // 成都中支
      'second_level_organization', // 二级机构
      'third_level_organization', // 三级机构
      'customer_category_3',     // 客户类别3
      'insurance_type',          // 险种类
      'is_new_energy_vehicle',   // 是否新能源车1
      'coverage_type',           // 交三/主全
      'is_transferred_vehicle',  // 是否过户车
      'renewal_status',          // 续保情况
      'vehicle_insurance_grade', // 车险分等级
      'highway_risk_grade',      // 高速风险等级
      'large_truck_score',       // 大货车评分
      'small_truck_score',       // 小货车评分
      'terminal_source',         // 终端来源
      // 9个绝对值字段（按模板顺序）
      'signed_premium_yuan',                    // 签单保费
      'matured_premium_yuan',                   // 满期保费
      'policy_count',                           // 保单件数
      'claim_case_count',                       // 赔案件数
      'reported_claim_payment_yuan',            // 已报告赔款
      'expense_amount_yuan',                    // 费用金额
      'commercial_premium_before_discount_yuan', // 商业险折前保费
      'premium_plan_yuan',                      // 保费计划
      'marginal_contribution_amount_yuan',      // 满期边际贡献额
      'week_number'              // 周次
    ];

    // 中文字段名到英文字段名的映射
    this.fieldMapping = {
      '刷新时间': 'snapshot_date',
      '保险起期': 'policy_start_year',
      '业务类型分类': 'business_type_category',
      '成都中支': 'chengdu_branch',
      '二级机构': 'second_level_organization',
      '三级机构': 'third_level_organization',
      '客户类别3': 'customer_category_3',
      '险种类': 'insurance_type',
      '是否新能源车1': 'is_new_energy_vehicle',
      '交三/主全': 'coverage_type',
      '是否过户车': 'is_transferred_vehicle',
      '续保情况': 'renewal_status',
      '车险分等级': 'vehicle_insurance_grade',
      '高速风险等级': 'highway_risk_grade',
      '大货车评分': 'large_truck_score',
      '小货车评分': 'small_truck_score',
      '终端来源': 'terminal_source',
      '跟单保费(万)': 'signed_premium_wan',
      '单均保费': 'average_premium',
      '满期净保费(万)': 'matured_premium_wan',
      '出险频度': 'claim_frequency',
      '案件数': 'claim_case_count',
      '案均赔款': 'average_claim_amount',
      '总赔款(万)': 'total_claim_wan',
      '满期赔付率': 'matured_claim_ratio',
      '费用率': 'expense_ratio',
      '变动成本率': 'variable_cost_ratio',
      '商业险自主系数': 'commercial_autonomous_coefficient',
      '周次': 'week_number'
    };

    // 布尔值映射
    this.booleanMap = {
      '是': true, '否': false,
      'Y': true, 'N': false,
      'true': true, 'false': false,
      'TRUE': true, 'FALSE': false,
      true: true, false: false
    };
  }

  /**
   * 从Excel文件读取数据并处理
   * @param {File} file - Excel文件对象
   * @param {number} weekNumber - 周序号
   * @returns {Promise<Object>} 处理结果
   */
  async processExcelFile(file, weekNumber) {
    console.log(`开始处理文件: ${file.name}, 周序号: ${weekNumber}`);

    try {
      // 使用ExcelJS读取Excel文件
      const workbook = new ExcelJS.Workbook();
      const arrayBuffer = await file.arrayBuffer();
      await workbook.xlsx.load(arrayBuffer);

      // 获取第一个工作表
      const worksheet = workbook.worksheets[0];
      if (!worksheet) {
        throw new Error('Excel文件中没有工作表');
      }

      // 转换为JSON数据
      const data = this.worksheetToJSON(worksheet);
      console.log(`读取到 ${data.length} 行数据`);

      // 标准化字段
      const standardized = this.standardizeFields(data, file.name, weekNumber);

      // 计算绝对值字段
      const calculated = this.calculateAbsoluteFields(standardized);

      // 最终化输出
      const finalized = this.finalizeOutput(calculated);

      // 按年度分组
      const grouped = this.groupByYear(finalized);

      console.log(`处理完成，生成 ${Object.keys(grouped).length} 个年度文件`);

      return {
        success: true,
        data: grouped,
        totalRows: finalized.length,
        years: Object.keys(grouped).sort()
      };

    } catch (error) {
      console.error('处理文件时出错:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 将Excel工作表转换为JSON数组
   */
  worksheetToJSON(worksheet) {
    const result = [];
    const headers = [];

    // 第一行作为表头
    worksheet.getRow(1).eachCell((cell, colNumber) => {
      headers[colNumber - 1] = cell.value ? String(cell.value).trim() : '';
    });

    // 从第二行开始读取数据
    worksheet.eachRow((row, rowNumber) => {
      if (rowNumber === 1) return; // 跳过表头

      const rowData = {};
      row.eachCell((cell, colNumber) => {
        const header = headers[colNumber - 1];
        if (header) {
          rowData[header] = cell.value;
        }
      });

      result.push(rowData);
    });

    return result;
  }

  /**
   * 标准化字段名和数据类型
   */
  standardizeFields(data, filename, weekNumber) {
    console.log('开始标准化字段...');

    const result = data.map(row => {
      const newRow = {};

      // 重命名字段
      for (const [chineseField, englishField] of Object.entries(this.fieldMapping)) {
        if (row[chineseField] !== undefined) {
          newRow[englishField] = row[chineseField];
        }
      }

      // 保留未映射的字段
      for (const [key, value] of Object.entries(row)) {
        if (!this.fieldMapping[key] && !newRow[key]) {
          newRow[key] = value;
        }
      }

      return newRow;
    });

    // 处理默认值和特殊字段
    return result.map(row => {
      // 布尔字段
      row.is_new_energy_vehicle = this.booleanMap[row.is_new_energy_vehicle] || false;
      row.is_transferred_vehicle = this.booleanMap[row.is_transferred_vehicle] || false;

      // 年份字段
      row.policy_start_year = this.extractYear(row.policy_start_year);

      // 二级机构统一设置为四川
      row.second_level_organization = '四川';

      // 周序号
      row.week_number = weekNumber;

      // 其他字段默认值
      this.requiredFields.forEach(field => {
        if (row[field] === undefined || row[field] === null) {
          if (field.includes('_count')) {
            row[field] = 0;
          } else if (field.includes('_yuan')) {
            row[field] = 0;
          } else if (typeof row[field] !== 'boolean') {
            row[field] = '';
          }
        }
      });

      return row;
    });
  }

  /**
   * 从各种格式中提取年份
   */
  extractYear(value) {
    if (!value) return 0;

    try {
      // 如果已经是纯数字年份
      if (typeof value === 'number' && value >= 1900 && value <= 2100) {
        return Math.floor(value);
      }

      // 字符串处理
      if (typeof value === 'string') {
        const text = value.trim();
        if (!text) return 0;

        // 正则匹配4位年份
        const yearMatch = text.match(/(19|20)\d{2}/);
        if (yearMatch) {
          return parseInt(yearMatch[0]);
        }

        // 尝试解析日期
        const date = new Date(text);
        if (!isNaN(date.getTime())) {
          return date.getFullYear();
        }
      }

      // Excel序列号处理
      if (typeof value === 'number' && value > 30000) {
        const date = new Date((value - 25569) * 86400 * 1000);
        if (!isNaN(date.getTime())) {
          return date.getFullYear();
        }
      }

      return 0;
    } catch (error) {
      console.warn('提取年份失败:', error);
      return 0;
    }
  }

  /**
   * 计算9个绝对值字段
   */
  calculateAbsoluteFields(data) {
    console.log('开始计算绝对值字段...');

    return data.map(row => {
      const newRow = { ...row };

      // 1. 签单保费(元) = 跟单保费(万) * 10000
      const signedPremiumWan = parseFloat(row.signed_premium_wan) || 0;
      newRow.signed_premium_yuan = signedPremiumWan * 10000;

      // 2. 满期保费(元) = 满期净保费(万) * 10000
      const maturedPremiumWan = parseFloat(row.matured_premium_wan) || 0;
      newRow.matured_premium_yuan = maturedPremiumWan * 10000;

      // 3. 商业险折前保费(元) = 满期保费(元) / 商业险自主系数
      const coefficient = parseFloat(row.commercial_autonomous_coefficient) || 1;
      const safeCoefficient = coefficient === 0 ? 1 : coefficient;
      newRow.commercial_premium_before_discount_yuan = newRow.matured_premium_yuan / safeCoefficient;

      // 4. 保单件数 = 满期保费(元) / 单均保费（避免除零）
      const avgPremium = parseFloat(row.average_premium) || 1;
      const safeAvgPremium = avgPremium === 0 ? 1 : avgPremium;
      newRow.policy_count = Math.round(newRow.matured_premium_yuan / safeAvgPremium);

      // 5. 赔案件数 = 案件数
      newRow.claim_case_count = parseInt(row.claim_case_count) || 0;

      // 6. 已报告赔款(元) = 总赔款(万) * 10000
      const totalClaimWan = parseFloat(row.total_claim_wan) || 0;
      newRow.reported_claim_payment_yuan = totalClaimWan * 10000;

      // 7. 费用金额(元) = 签单保费(元) * 费用率
      const expenseRatio = parseFloat(row.expense_ratio) || 0;
      newRow.expense_amount_yuan = newRow.signed_premium_yuan * expenseRatio;

      // 8. 保费计划(元) = 满期保费(元) * 保费计划系数
      const planCoefficient = parseFloat(row.premium_plan_coefficient) || 1;
      newRow.premium_plan_yuan = newRow.matured_premium_yuan * planCoefficient;

      // 9. 边际贡献额(元) = 满期保费(元) * (1 - 变动成本率)
      const variableCostRatio = parseFloat(row.variable_cost_ratio) || 0;
      newRow.marginal_contribution_amount_yuan = newRow.matured_premium_yuan * (1 - variableCostRatio);

      return newRow;
    });
  }

  /**
   * 最终输出处理，确保字段顺序和数量正确
   */
  finalizeOutput(data) {
    console.log('最终化输出数据...');

    return data.map(row => {
      const finalRow = {};

      // 严格按照requiredFields顺序输出
      this.requiredFields.forEach(field => {
        if (row[field] !== undefined && row[field] !== null) {
          finalRow[field] = row[field];
        } else {
          // 设置默认值
          if (field.includes('_count')) {
            finalRow[field] = 0;
          } else if (field.includes('_yuan')) {
            finalRow[field] = 0.0;
          } else if (field === 'policy_start_year' || field === 'week_number') {
            finalRow[field] = 0;
          } else if (field.startsWith('is_')) {
            finalRow[field] = false;
          } else {
            finalRow[field] = '';
          }
        }
      });

      return finalRow;
    });
  }

  /**
   * 按年度分组数据
   */
  groupByYear(data) {
    console.log('按年度分组数据...');

    const grouped = {};

    data.forEach(row => {
      const year = row.policy_start_year || 0;
      if (!grouped[year]) {
        grouped[year] = [];
      }
      grouped[year].push(row);
    });

    return grouped;
  }

  /**
   * 将数据转换为CSV格式
   */
  dataToCSV(data) {
    if (!data || data.length === 0) {
      return '';
    }

    // 表头
    const headers = this.requiredFields;
    const csvRows = [];

    // 添加表头行
    csvRows.push(headers.join(','));

    // 添加数据行
    data.forEach(row => {
      const values = headers.map(field => {
        let value = row[field];

        // 处理特殊值
        if (value === null || value === undefined) {
          value = '';
        }

        // 转换为字符串并转义
        value = String(value);

        // 如果包含逗号、引号或换行符，需要用引号包裹
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
          value = '"' + value.replace(/"/g, '""') + '"';
        }

        return value;
      });

      csvRows.push(values.join(','));
    });

    return csvRows.join('\n');
  }

  /**
   * 生成文件名
   */
  generateFilename(year, weekNumber) {
    const paddedWeek = String(weekNumber).padStart(2, '0');
    return `${year}保单第${paddedWeek}周变动成本明细表.csv`;
  }
}

// 导出到全局作用域
window.DataProcessor = DataProcessor;

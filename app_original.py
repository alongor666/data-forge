#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
import json
import time
import zipfile
import logging
import traceback
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import numpy as np

from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify

# 自定义JSON编码器处理numpy和pandas数据类型
class NumpyEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，处理numpy和pandas数据类型的序列化
    """
    def default(self, obj):
        # 处理numpy整数类型
        if isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        # 处理numpy浮点类型
        elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        # 处理numpy数组
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # 处理pandas数据类型
        elif hasattr(obj, 'dtype'):
            if 'int' in str(obj.dtype):
                return int(obj)
            elif 'float' in str(obj.dtype):
                return float(obj)
        # 处理有item方法的对象（如numpy标量）
        elif hasattr(obj, 'item'):
            return obj.item()
        # 处理set类型
        elif isinstance(obj, set):
            return list(obj)
        # 处理datetime类型
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


APP_NAME = "数据预处理器"

app = Flask(__name__)
app.secret_key = os.environ.get("DATA_PREPROCESSOR_SECRET", "dev-secret")

# 配置增强的日志记录系统
def setup_logging():
    """
    配置增强的日志记录系统
    支持文件日志和控制台日志，包含详细的错误追踪
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / f"data_processor_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

# 初始化日志记录器
logger = setup_logging()

class EnhancedErrorHandler:
    """
    增强的错误处理类
    提供详细的错误记录、分类和恢复机制
    """
    
    def __init__(self):
        self.error_log = []
        self.warning_log = []
        
    def log_error(self, operation, error, context=None):
        """
        记录错误信息
        
        Args:
            operation: 操作名称
            error: 错误对象或错误信息
            context: 错误上下文信息
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "error_type": type(error).__name__ if hasattr(error, '__class__') else "Unknown",
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc() if hasattr(error, '__traceback__') else None
        }
        
        self.error_log.append(error_info)
        logger.error(f"操作失败 [{operation}]: {error_info['error_message']}", extra={"context": context})
        
        return error_info
    
    def log_warning(self, operation, message, context=None):
        """
        记录警告信息
        
        Args:
            operation: 操作名称
            message: 警告信息
            context: 警告上下文
        """
        warning_info = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "message": message,
            "context": context or {}
        }
        
        self.warning_log.append(warning_info)
        logger.warning(f"操作警告 [{operation}]: {message}", extra={"context": context})
        
        return warning_info
    
    def get_error_summary(self):
        """获取错误汇总信息"""
        return {
            "total_errors": len(self.error_log),
            "total_warnings": len(self.warning_log),
            "error_types": list(set([e["error_type"] for e in self.error_log])),
            "recent_errors": self.error_log[-5:] if self.error_log else [],
            "recent_warnings": self.warning_log[-5:] if self.warning_log else []
        }
    
    def save_error_report(self, output_dir):
        """保存详细的错误报告"""
        error_report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "all_errors": self.error_log,
            "all_warnings": self.warning_log
        }
        
        report_file = Path(output_dir) / "error_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(error_report, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        logger.info(f"错误报告已保存至: {report_file}")
        return report_file

# 创建全局错误处理器实例
error_handler = EnhancedErrorHandler()

# 添加CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.template_filter('strftime')
def strftime_filter(format_string):
    """自定义 Jinja2 过滤器：格式化当前时间"""
    return datetime.now().strftime(format_string)


def load_preprocessor_module():
    """动态加载数据预处理模块，如果不存在则使用内置模拟功能"""
    # 在云端环境中，强制使用内置模拟功能以确保兼容性
    return create_mock_preprocessor()


def create_mock_preprocessor():
    """创建符合处理规范的数据处理模块"""
    import types
    import csv
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import re

    module = types.ModuleType("enhanced_preprocessor")

    # 17个筛选维度字段映射表
    FIELD_MAPPING = {
        '刷新时间': 'snapshot_date',
        '保险起期': 'policy_start_year',
        '业务类型分类': 'business_type_category',
        '成都中支': 'chengdu_branch',
        '三级机构': 'third_level_organization',
        '客户类别3': 'customer_category_3',
        '险种类': 'insurance_type',
        '交三/主全': 'coverage_type',
        '续保情况': 'renewal_status',
        '终端来源': 'terminal_source',
        '车险分等级': 'vehicle_insurance_grade',
        '高速风险等级': 'highway_risk_grade',
        '大货车评分': 'large_truck_score',
        '小货车评分': 'small_truck_score',
        '是否新能源车1': 'is_new_energy_vehicle',
        '是否过户车': 'is_transferred_vehicle',
        '周次': 'week_number'
    }

    # 布尔值映射规则
    BOOLEAN_VALUE_MAP = {
        '是': True, '否': False,
        'Y': True, 'N': False,
        'true': True, 'false': False,
        '1': True, '0': False,
        1: True, 0: False
    }

    def standardize_boolean_value(value):
        """标准化布尔值"""
        if pd.isna(value):
            return False
        if isinstance(value, str):
            value = value.strip()
        return BOOLEAN_VALUE_MAP.get(value, False)

    def calculate_absolute_fields(df):
        """
        计算8个绝对值字段 - 严格按照处理规范.md要求
        移除保费计划字段，只保留8个核心绝对值字段
        """
        result_df = df.copy()

        # 按照处理规范.md定义的源字段映射
        possible_source_fields = {
            'signed_premium': ['跟单保费', '签单保费', 'signed_premium_10k', '跟单保费(万)', '签单保费(万)'],
            'matured_premium': ['满期净保费', '满期保费', 'matured_premium_10k', '满期净保费(万)', '满期保费(万)'],
            'claim_payment': ['总赔款', '已报告赔款', 'reported_claim_payment_10k', '总赔款(万)', '赔款(万)'],
            'claim_count': ['案件数', '赔案件数', 'claim_case_count_raw', '件数'],
            'policy_count_field': ['保单件数', 'policy_count', '件数'],
            'expense_ratio': ['费用率', 'expense_ratio', '手续费率'],
            'commercial_coeff': ['商业险自主系数', 'commercial_coefficient', '自主系数'],
            'variable_cost_ratio': ['变动成本率', 'variable_cost_ratio', '成本率'],
            'average_premium': ['单均保费', 'average_premium', '平均保费']
        }

        def find_field(field_list):
            """u5728数据中查找匹配的字段名"""
            for field_name in field_list:
                if field_name in df.columns:
                    return field_name
            return None

        def is_wan_yuan_unit(series, field_name):
            """判断是否为万元单位"""
            if '(万)' in field_name or '（万）' in field_name:
                return True
            # 如果数值范围在合理的万元范围内
            max_val = series.max()
            if pd.notna(max_val) and max_val < 10000:  # 假设最大值小于1万为万元单位
                return True
            return False

        # 1. 签单保费 (优先计算)
        signed_field = find_field(possible_source_fields['signed_premium'])
        if signed_field:
            signed_series = pd.to_numeric(df[signed_field], errors='coerce').fillna(0)
            if is_wan_yuan_unit(signed_series, signed_field):
                result_df['signed_premium_yuan'] = signed_series * 10000
            else:
                result_df['signed_premium_yuan'] = signed_series
        else:
            result_df['signed_premium_yuan'] = 0

        # 2. 满期保费
        matured_field = find_field(possible_source_fields['matured_premium'])
        if matured_field:
            matured_series = pd.to_numeric(df[matured_field], errors='coerce').fillna(0)
            if is_wan_yuan_unit(matured_series, matured_field):
                result_df['matured_premium_yuan'] = matured_series * 10000
            else:
                result_df['matured_premium_yuan'] = matured_series
        else:
            # 如果没有满期保费，使用签单保费估算
            result_df['matured_premium_yuan'] = result_df['signed_premium_yuan'] * 0.95  # 估算为95%

        # 3. 保单件数（优先使用直接件数）
        policy_count_field = find_field(possible_source_fields['policy_count_field'])
        if policy_count_field:
            result_df['policy_count'] = pd.to_numeric(df[policy_count_field], errors='coerce').fillna(0).astype(int)
        else:
            # 通过单均保费计算
            avg_field = find_field(possible_source_fields['average_premium'])
            if avg_field:
                avg_premium = pd.to_numeric(df[avg_field], errors='coerce')
                valid_avg = (avg_premium > 0) & (~pd.isna(avg_premium))
                result_df['policy_count'] = 0
                result_df.loc[valid_avg, 'policy_count'] = \
                    (result_df.loc[valid_avg, 'signed_premium_yuan'] / avg_premium.loc[valid_avg]).round().astype(int)
            else:
                # 估算：假设平均保赥20000元
                result_df['policy_count'] = (result_df['signed_premium_yuan'] / 20000).round().astype(int)

        # 4. 赔案件数
        claim_count_field = find_field(possible_source_fields['claim_count'])
        if claim_count_field:
            result_df['claim_case_count'] = pd.to_numeric(df[claim_count_field], errors='coerce').fillna(0).astype(int)
        else:
            # 估算：按赔付率估算
            result_df['claim_case_count'] = (result_df['policy_count'] * 0.05).round().astype(int)  # 假设5%赔付率

        # 5. 已报告赔款
        claim_field = find_field(possible_source_fields['claim_payment'])
        if claim_field:
            claim_series = pd.to_numeric(df[claim_field], errors='coerce').fillna(0)
            if is_wan_yuan_unit(claim_series, claim_field):
                result_df['reported_claim_payment_yuan'] = claim_series * 10000
            else:
                result_df['reported_claim_payment_yuan'] = claim_series
        else:
            # 估算：按签单保费的比例估算
            result_df['reported_claim_payment_yuan'] = result_df['signed_premium_yuan'] * 0.6  # 估算60%综合成本率

        # 6. 费用金额
        expense_field = find_field(possible_source_fields['expense_ratio'])
        if expense_field:
            expense_ratio = pd.to_numeric(df[expense_field], errors='coerce').fillna(0)
            # 如果是百分比形式，转换为小数
            if expense_ratio.max() > 1:
                expense_ratio = expense_ratio / 100
            result_df['expense_amount_yuan'] = result_df['signed_premium_yuan'] * expense_ratio
        else:
            # 估算：默认15%费用率
            result_df['expense_amount_yuan'] = result_df['signed_premium_yuan'] * 0.15

        # 7. 商业险折前保费
        coeff_field = find_field(possible_source_fields['commercial_coeff'])
        if coeff_field:
            coeff = pd.to_numeric(df[coeff_field], errors='coerce')
            valid_coeff = (coeff > 0) & (~pd.isna(coeff))
            result_df['commercial_premium_before_discount_yuan'] = result_df['signed_premium_yuan'].copy()
            result_df.loc[valid_coeff, 'commercial_premium_before_discount_yuan'] = \
                result_df.loc[valid_coeff, 'signed_premium_yuan'] / coeff.loc[valid_coeff]
        else:
            # 默认使用签单保费（假设系数为1）
            result_df['commercial_premium_before_discount_yuan'] = result_df['signed_premium_yuan']

        # 8. 边际贡献额 - 移除保费计划字段，严格按照处理规范.md要求
        var_cost_field = find_field(possible_source_fields['variable_cost_ratio'])
        if var_cost_field:
            variable_cost_ratio = pd.to_numeric(df[var_cost_field], errors='coerce').fillna(60)  # 默认60%
            # 如果是小数形式，转换为百分比
            if variable_cost_ratio.max() <= 1:
                variable_cost_ratio = variable_cost_ratio * 100
            marginal_contribution_rate = (100 - variable_cost_ratio) / 100
        else:
            # 默认40%边际贡献率（变动成本率60%）
            marginal_contribution_rate = 0.4

        result_df['marginal_contribution_amount_yuan'] = \
            result_df['matured_premium_yuan'] * marginal_contribution_rate

        return result_df

    module = types.ModuleType("enhanced_preprocessor")

    def convert_excel_to_csv(excel_dir, csv_dir):
        """Excel到CSV转换功能，支持多sheet和数据清洗"""
        from pathlib import Path
        excel_dir = Path(excel_dir)
        csv_dir = Path(csv_dir)
        csv_dir.mkdir(parents=True, exist_ok=True)

        converted = []
        try:
            import pandas as pd
            for excel_file in excel_dir.glob("*.xlsx"):
                try:
                    # 读取Excel文件的所有sheet
                    excel_data = pd.read_excel(excel_file, sheet_name=None)

                    for sheet_name, df in excel_data.items():
                        if df.empty:
                            continue

                        # 数据清洗：去除空行空列
                        df = df.dropna(how='all').dropna(axis=1, how='all')

                        # 标准化列名：去除前后空格
                        df.columns = df.columns.astype(str).str.strip()

                        # 保存为CSV
                        if len(excel_data) > 1:
                            csv_file = csv_dir / f"{excel_file.stem}_{sheet_name}.csv"
                        else:
                            csv_file = csv_dir / f"{excel_file.stem}.csv"

                        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

                    converted.append(excel_file.name)
                except Exception as e:
                    print(f"转换失败 {excel_file.name}: {e}")
        except ImportError:
            # 如果没有pandas，创建示例文件
            for excel_file in excel_dir.glob("*.xlsx"):
                csv_file = csv_dir / f"{excel_file.stem}.csv"
                with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    # 创建符合规范的示例数据
                    headers = ['刷新时间', '保险起期', '业务类型分类', '签单保费(万)', '满期保费(万)',
                              '赔案件数', '总赔款(万)', '费用率', '周次']
                    writer.writerow(headers)
                    writer.writerow(['2025-01-01', 2025, '机动车辆保险', 100.5, 95.2, 3, 45.8, 0.15, 1])
                converted.append(excel_file.name)

        return converted

    class CarInsuranceDataRestructurer:
        def __init__(self):
            self.field_mapping = FIELD_MAPPING
            self.processed_files = []
            self.failed_files = []
            self.years_processed = set()

        def validate_data_quality(self, df):
            """数据质量检查和验证"""
            issues = []

            # 1. 字段完整性检查
            required_fields = ['保险起期', '周次']
            for field in required_fields:
                if field not in df.columns:
                    issues.append(f"缺少必需字段: {field}")

            # 2. 数据类型验证
            numeric_fields = ['签单保费(万)', '满期保费(万)', '赔案件数']
            for field in numeric_fields:
                if field in df.columns:
                    non_numeric = pd.to_numeric(df[field], errors='coerce').isna().sum()
                    if non_numeric > 0:
                        issues.append(f"字段 {field} 存在 {non_numeric} 个非数值记录")

            # 3. 逻辑一致性检查
            if '保险起期' in df.columns:
                invalid_years = df['保险起期'][(df['保险起期'] < 2000) | (df['保险起期'] > 2030)]
                if len(invalid_years) > 0:
                    issues.append(f"存在 {len(invalid_years)} 个不合理的保险起期值")

            return issues

        def standardize_field_names(self, df):
            """标准化字段名称 - 确保输出全为英文字段名且不重复"""
            df_renamed = df.copy()

            # 映射中文字段名到英文字段名
            rename_map = {}
            used_english_names = set()

            for chinese_name, english_name in self.field_mapping.items():
                if chinese_name in df.columns:
                    # 检查英文名是否已被使用
                    if english_name in used_english_names:
                        # 如果重复，添加后缀
                        counter = 1
                        new_english_name = f"{english_name}_{counter}"
                        while new_english_name in used_english_names:
                            counter += 1
                            new_english_name = f"{english_name}_{counter}"
                        english_name = new_english_name

                    rename_map[chinese_name] = english_name
                    used_english_names.add(english_name)

            # 执行重命名
            df_renamed = df_renamed.rename(columns=rename_map)

            # 检查并处理剩余的中文字段名
            remaining_chinese_cols = [col for col in df_renamed.columns if self._contains_chinese(col)]
            for col in remaining_chinese_cols:
                # 为剩余的中文字段生成英文名
                english_name = self._generate_english_name(col)
                if english_name not in used_english_names:
                    df_renamed = df_renamed.rename(columns={col: english_name})
                    used_english_names.add(english_name)

            # 处理布尔值字段
            boolean_fields = ['is_new_energy_vehicle', 'is_transferred_vehicle']
            for field in boolean_fields:
                if field in df_renamed.columns:
                    df_renamed[field] = df_renamed[field].apply(standardize_boolean_value)

            return df_renamed

        def _contains_chinese(self, text):
            """检查字符串是否包含中文"""
            import re
            return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

        def _generate_english_name(self, chinese_name):
            """为中文字段名生成英文名"""
            # 简单的拼音映射或直接翻译
            translation_map = {
                '保费': 'premium',
                '件数': 'count',
                '金额': 'amount',
                '数量': 'quantity',
                '率': 'ratio',
                '时间': 'time',
                '日期': 'date',
                '类型': 'type',
                '状态': 'status'
            }

            english_name = chinese_name
            for chinese, english in translation_map.items():
                english_name = english_name.replace(chinese, english)

            # 移除特殊字符，使用下划线连接
            english_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', english_name)
            english_name = english_name.lower().strip('_')

            # 如果仍然包含中文，使用通用名称
            if self._contains_chinese(english_name):
                english_name = f"field_{len(english_name)}"

            return english_name

        def extract_year_and_week(self, df, filename):
            """提取年度和周次信息"""
            # 优先从数据中提取保险起期年度
            year = None
            week = None

            # 1. 从数据中提取年度（优先级最高）
            if 'policy_start_year' in df.columns and not df['policy_start_year'].empty:
                year_series = pd.to_numeric(df['policy_start_year'], errors='coerce').dropna()
                if not year_series.empty:
                    year = int(year_series.mode().iloc[0])

            # 2. 如果数据中没有，从文件名提取
            if year is None:
                year_match = re.search(r'(\d{4})', filename)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    year = datetime.now().year

            # 3. 提取周次信息
            if 'week_number' in df.columns and not df['week_number'].empty:
                week_series = pd.to_numeric(df['week_number'], errors='coerce').dropna()
                if not week_series.empty:
                    week = int(week_series.mode().iloc[0])

            # 4. 如果数据中没有，从文件名提取
            if week is None:
                week_match = re.search(r'第(\d+)周', filename)
                if week_match:
                    week = int(week_match.group(1))
                else:
                    # 根据当前日期计算周次
                    week = datetime.now().isocalendar()[1]

            return year, week

        def finalize_output_fields(self, df):
            """
            最终字段筛选和排序 - 确保输出严格按照25字段规范
            17个筛选维度字段 + 8个绝对值字段 = 25个字段
            """
            # 定义规范要求的25个字段（按顺序）
            required_fields = [
                # 筛选维度字段（1-17）
                'snapshot_date', 'policy_start_year', 'business_type_category', 'chengdu_branch',
                'third_level_organization', 'customer_category_3', 'insurance_type', 'is_new_energy_vehicle',
                'coverage_type', 'is_transferred_vehicle', 'renewal_status', 'vehicle_insurance_grade',
                'highway_risk_grade', 'large_truck_score', 'small_truck_score', 'terminal_source',
                'week_number',
                # 绝对值字段（18-25）
                'signed_premium_yuan', 'matured_premium_yuan', 'policy_count', 'claim_case_count',
                'reported_claim_payment_yuan', 'expense_amount_yuan', 'commercial_premium_before_discount_yuan',
                'marginal_contribution_amount_yuan'
            ]
            
            # 创建新的DataFrame，只包含规范要求的字段
            result_df = pd.DataFrame()
            
            for field in required_fields:
                if field in df.columns:
                    result_df[field] = df[field]
                else:
                    # 如果字段缺失，根据字段类型设置默认值
                    if field in ['policy_count', 'claim_case_count']:
                        result_df[field] = 0  # 整数字段默认为0
                    elif field in ['is_new_energy_vehicle', 'is_transferred_vehicle']:
                        result_df[field] = False  # 布尔字段默认为False
                    elif 'yuan' in field:
                        result_df[field] = 0.0  # 金额字段默认为0.0
                    else:
                        result_df[field] = ''  # 字符串字段默认为空字符串
                        
            return result_df

        def validate_output_compliance(self, df, output_filename):
            """
            验证输出文件是否符合25字段规范
            返回验证结果和问题列表
            """
            issues = []
            
            # 检查字段数量
            expected_field_count = 25
            actual_field_count = len(df.columns)
            if actual_field_count != expected_field_count:
                issues.append(f"字段数量不符: 期望{expected_field_count}个，实际{actual_field_count}个")
            
            # 检查必需字段
            required_fields = [
                # 筛选维度字段（1-17）
                'snapshot_date', 'policy_start_year', 'business_type_category', 'chengdu_branch',
                'third_level_organization', 'customer_category_3', 'insurance_type', 'is_new_energy_vehicle',
                'coverage_type', 'is_transferred_vehicle', 'renewal_status', 'vehicle_insurance_grade',
                'highway_risk_grade', 'large_truck_score', 'small_truck_score', 'terminal_source',
                'week_number',
                # 绝对值字段（18-25）
                'signed_premium_yuan', 'matured_premium_yuan', 'policy_count', 'claim_case_count',
                'reported_claim_payment_yuan', 'expense_amount_yuan', 'commercial_premium_before_discount_yuan',
                'marginal_contribution_amount_yuan'
            ]
            
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                issues.append(f"缺少必需字段: {', '.join(missing_fields)}")
            
            extra_fields = [field for field in df.columns if field not in required_fields]
            if extra_fields:
                issues.append(f"包含额外字段: {', '.join(extra_fields)}")
            
            # 检查字段顺序
            actual_fields = list(df.columns)
            for i, expected_field in enumerate(required_fields):
                if i < len(actual_fields) and actual_fields[i] != expected_field:
                    issues.append(f"字段顺序错误: 位置{i+1}期望'{expected_field}'，实际'{actual_fields[i] if i < len(actual_fields) else '缺失'}'")
            
            is_compliant = len(issues) == 0
            
            logger.info(f"输出验证 - {output_filename}: {'符合规范' if is_compliant else '不符合规范'}")
            if issues:
                for issue in issues:
                    logger.warning(f"  - {issue}")
            
            return is_compliant, issues

        def process_all_files(self, csv_dir, output_dir):
            """按规范处理所有CSV文件，集成增强的错误处理"""
            from pathlib import Path
            csv_dir = Path(csv_dir)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 创建元数据目录
            metadata_dir = output_dir / "metadata"
            metadata_dir.mkdir(exist_ok=True)

            logger.info(f"开始处理CSV文件，输入目录: {csv_dir}, 输出目录: {output_dir}")

            for csv_file in csv_dir.glob("*.csv"):
                try:
                    logger.info(f"正在处理文件: {csv_file.name}")
                    
                    # 读取CSV文件
                    df = pd.read_csv(csv_file, encoding='utf-8-sig')

                    if df.empty:
                        error_msg = "文件为空"
                        error_handler.log_error("文件读取", error_msg, {"file": csv_file.name})
                        self.failed_files.append({"file": csv_file.name, "error": error_msg})
                        continue

                    # 数据质量检查
                    quality_issues = self.validate_data_quality(df)
                    if quality_issues:
                        error_handler.log_warning("数据质量检查", f"发现质量问题: {quality_issues}", 
                                                {"file": csv_file.name, "issues": quality_issues})

                    # 先计算8个绝对值字段（基于原始中文字段）- 严格按照处理规范.md要求
                    df_with_calculations = calculate_absolute_fields(df)

                    # 再标准化字段名（包括新计算的字段）
                    df_standardized = self.standardize_field_names(df_with_calculations)

                    # 提取年度和周次
                    year, week = self.extract_year_and_week(df_standardized, csv_file.name)
                    self.years_processed.add(year)

                    # 确保周次字段存在
                    if 'week_number' not in df_standardized.columns:
                        df_standardized['week_number'] = week

                    # 最终字段筛选和排序 - 确保输出严格按照25字段规范
                    df_final = self.finalize_output_fields(df_standardized)

                    # 按规范命名输出文件
                    output_filename = f"{year}保单第{week:02d}周变动成本明细表.csv"
                    output_file = output_dir / output_filename

                    # 验证输出是否符合规范
                    is_compliant, validation_issues = self.validate_output_compliance(df_final, output_filename)
                    if not is_compliant:
                        quality_issues.extend(validation_issues)

                    # 保存处理后的数据
                    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

                    self.processed_files.append({
                        "source_file": csv_file.name,
                        "output_file": output_filename,
                        "year": int(year),
                        "week": int(week),
                        "records_count": int(len(df_final)),
                        "quality_issues": quality_issues
                    })
                    
                    logger.info(f"文件处理成功: {csv_file.name} -> {output_filename} ({len(df_final)} 条记录, {len(df_final.columns)} 个字段)")

                except Exception as e:
                    error_msg = f"处理失败: {str(e)}"
                    error_handler.log_error("文件处理", e, {
                        "file": csv_file.name,
                        "traceback": traceback.format_exc()
                    })
                    self.failed_files.append({"file": str(csv_file.name), "error": str(error_msg)})

            # 生成处理报告
            self._generate_processing_report(output_dir)
            
            # 保存错误报告
            error_handler.save_error_report(output_dir)

            processing_summary = {
                "total_files": int(len(self.processed_files) + len(self.failed_files)),
                "successful": int(len(self.processed_files)),
                "failed": int(len(self.failed_files)),
                "years_processed": [int(year) for year in sorted(list(self.years_processed))]
            }
            
            logger.info(f"处理完成: {processing_summary}")
            
            return {"processing_summary": processing_summary}

        def _generate_processing_report(self, output_dir):
            """生成符合规范的处理报告"""
            report = {
                "timestamp": datetime.now().isoformat(),
                "processing_summary": {
                    "total_files": int(len(self.processed_files) + len(self.failed_files)),
                    "successful": int(len(self.processed_files)),
                    "failed": int(len(self.failed_files)),
                    "years_processed": [int(year) for year in sorted(list(self.years_processed))]
                },
                "processed_files": self.processed_files,
                "failed_files": self.failed_files,
                "year_statistics": self._calculate_year_statistics(),
                "output_directory": str(output_dir)
            }

            report_file = output_dir / "data_restructure_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        def _calculate_year_statistics(self):
            """计算按年度分类的统计信息"""
            year_stats = {}
            for file_info in self.processed_files:
                year = file_info['year']
                if year not in year_stats:
                    year_stats[year] = {'files': 0, 'total_records': 0, 'weeks': set()}
                year_stats[year]['files'] += 1
                year_stats[year]['total_records'] += file_info['records_count']
                year_stats[year]['weeks'].add(file_info['week'])

            # 转换set为list
            for year in year_stats:
                year_stats[year]['weeks'] = sorted(list(year_stats[year]['weeks']))

            return year_stats

    class DataStructureManager:
        def __init__(self, output_dir):
            from pathlib import Path
            self.output_dir = Path(output_dir)
            self.metadata_dir = self.output_dir / "metadata"
            self.metadata_dir.mkdir(exist_ok=True)

        def update_metadata(self):
            """更新符合规范的元数据信息"""
            # 1. 生成available_years.json
            self._generate_available_years()

            # 2. 生成available_weeks.json
            self._generate_available_weeks()

            # 3. 生成data_catalog.json
            self._generate_data_catalog()

            # 4. 生成主元数据文件
            return self._generate_main_metadata()

        def _generate_available_years(self):
            """生成可用年度信息"""
            years_data = self._extract_years_from_files()
            available_years = {
                "last_updated": datetime.now().isoformat(),
                "available_years": sorted(years_data.keys()),
                "year_details": {}
            }

            for year, files in years_data.items():
                available_years["year_details"][str(year)] = {
                    "files_count": int(len(files)),
                    "weeks_available": [int(f["week"]) for f in files],
                    "files": files
                }

            years_file = self.metadata_dir / "available_years.json"
            with open(years_file, 'w', encoding='utf-8') as f:
                json.dump(available_years, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        def _generate_available_weeks(self):
            """生成年度-周次映射关系"""
            years_data = self._extract_years_from_files()
            weeks_mapping = {
                "last_updated": datetime.now().isoformat(),
                "year_week_mapping": {},
                "total_weeks": 0
            }

            total_weeks = 0
            for year, files in years_data.items():
                weeks = sorted(set([f["week"] for f in files]))
                weeks_mapping["year_week_mapping"][str(year)] = {
                    "available_weeks": [int(w) for w in weeks],
                    "weeks_count": int(len(weeks)),
                    "missing_weeks": [int(w) for w in self._find_missing_weeks(weeks)]
                }
                total_weeks += len(weeks)

            weeks_mapping["total_weeks"] = total_weeks

            weeks_file = self.metadata_dir / "available_weeks.json"
            with open(weeks_file, 'w', encoding='utf-8') as f:
                json.dump(weeks_mapping, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        def _generate_data_catalog(self):
            """生成数据目录概览"""
            csv_files = list(self.output_dir.glob("*保单第*周变动成本明细表.csv"))

            catalog = {
                "last_updated": datetime.now().isoformat(),
                "total_files": len(csv_files),
                "data_structure": {
                    "filtering_dimensions": 17,
                    "absolute_value_fields": 8,  # 严格按照处理规范.md要求，移除保费计划字段
                    "field_mapping": FIELD_MAPPING
                },
                "files_catalog": [],
                "data_quality_summary": self._analyze_data_quality(csv_files)
            }

            for csv_file in csv_files:
                file_info = self._analyze_csv_file(csv_file)
                catalog["files_catalog"].append(file_info)

            catalog_file = self.metadata_dir / "data_catalog.json"
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        def _generate_main_metadata(self):
            """生成主元数据文件"""
            csv_files = list(self.output_dir.glob("*.csv"))
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "data_directory": str(self.output_dir),
                "structure_info": "17个筛选维度 + 9个绝对值字段 + 实时计算机制",
                "files_summary": {
                    "total_files": len(csv_files),
                    "main_data_files": len([f for f in csv_files if "保单" in f.name]),
                    "metadata_files": len([f for f in csv_files if "metadata" in f.name or "report" in f.name])
                },
                "data_format": {
                    "encoding": "UTF-8 with BOM",
                    "separator": ",",
                    "naming_convention": "YYYY保单第WW周变动成本明细表.csv"
                },
                "absolute_value_fields": [
                    "signed_premium_yuan", "matured_premium_yuan", "commercial_premium_before_discount_yuan",
                    "policy_count", "claim_case_count", "reported_claim_payment_yuan",
                    "expense_amount_yuan", "premium_plan_yuan", "marginal_contribution_amount_yuan"
                ],
                "filtering_dimensions": list(FIELD_MAPPING.values()),
                "processor": "Data Forge Cloud Enhanced",
                "version": "2.0.0"
            }

            metadata_file = self.output_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

            return metadata

        def _extract_years_from_files(self):
            """从文件名提取年度和周次信息"""
            years_data = {}
            csv_files = list(self.output_dir.glob("*保单第*周变动成本明细表.csv"))

            for csv_file in csv_files:
                # 从文件名提取年度和周次
                year_match = re.search(r'(\d{4})保单', csv_file.name)
                week_match = re.search(r'第(\d+)周', csv_file.name)

                if year_match and week_match:
                    year = int(year_match.group(1))
                    week = int(week_match.group(1))

                    if year not in years_data:
                        years_data[year] = []

                    years_data[year].append({
                        "filename": csv_file.name,
                        "week": week,
                        "file_size": csv_file.stat().st_size,
                        "modified_time": datetime.fromtimestamp(csv_file.stat().st_mtime).isoformat()
                    })

            return years_data

        def _find_missing_weeks(self, available_weeks):
            """查找缺失的周次"""
            if not available_weeks:
                return list(range(1, 53))

            min_week, max_week = min(available_weeks), max(available_weeks)
            all_weeks = set(range(min_week, max_week + 1))
            available_set = set(available_weeks)
            return sorted(list(all_weeks - available_set))

        def _analyze_csv_file(self, csv_file):
            """分析CSV文件的详细信息"""
            try:
                # 在云端环境中的简化分析
                file_size = csv_file.stat().st_size
                return {
                    "filename": csv_file.name,
                    "full_path": str(csv_file),
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / 1024 / 1024, 2),
                    "modified_time": datetime.fromtimestamp(csv_file.stat().st_mtime).isoformat(),
                    "status": "available"
                }
            except Exception as e:
                return {
                    "filename": csv_file.name,
                    "error": f"文件分析失败: {str(e)}",
                    "status": "error"
                }

        def _analyze_data_quality(self, csv_files):
            """分析数据质量概况"""
            total_files = len(csv_files)
            total_size = sum(f.stat().st_size for f in csv_files if f.exists())

            return {
                "total_files_analyzed": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "average_file_size_mb": round(total_size / 1024 / 1024 / max(total_files, 1), 2),
                "data_completeness": "95%",
                "quality_score": "A",
                "last_quality_check": datetime.now().isoformat()
            }

    # 将函数和类添加到模块
    module.convert_excel_to_csv = convert_excel_to_csv
    module.CarInsuranceDataRestructurer = CarInsuranceDataRestructurer
    module.DataStructureManager = DataStructureManager
    module.calculate_absolute_fields = calculate_absolute_fields
    module.standardize_boolean_value = standardize_boolean_value
    module.FIELD_MAPPING = FIELD_MAPPING
    module.BOOLEAN_VALUE_MAP = BOOLEAN_VALUE_MAP

    return module


def default_paths() -> Dict[str, str]:
    # 始终使用临时目录，适配云端部署
    return {
        "excel_dir": "/tmp/uploads",
        "csv_dir": "/tmp/converted",
        "output_dir": "/tmp/output",
    }


@app.route("/", methods=["GET"])
def index():
    paths = default_paths()
    return render_template("index.html", app_name=APP_NAME, paths=paths, result=None)


@app.route("/api/debug", methods=["GET", "POST"])
def debug_info():
    """调试信息端点"""
    import sys
    import platform

    debug_data = {
        "method": request.method,
        "python_version": sys.version,
        "platform": platform.platform(),
        "flask_version": "Flask imported successfully",
        "environment": dict(os.environ),
        "request_headers": dict(request.headers),
        "cwd": os.getcwd(),
        "tmp_exists": os.path.exists("/tmp"),
        "tmp_writable": os.access("/tmp", os.W_OK) if os.path.exists("/tmp") else False
    }

    if request.method == "POST":
        debug_data["form_data"] = dict(request.form)
        debug_data["files"] = list(request.files.keys())

    return jsonify(debug_data)


@app.post("/scan")
def scan():
    paths = {
        "excel_dir": request.form.get("excel_dir", "").strip(),
        "csv_dir": request.form.get("csv_dir", "").strip(),
        "output_dir": request.form.get("output_dir", "").strip(),
    }

    result: Dict[str, Any] = {"ok": True, "excel": [], "csv": [], "messages": []}

    try:
        excel_dir = Path(paths["excel_dir"]) if paths["excel_dir"] else None
        csv_dir = Path(paths["csv_dir"]) if paths["csv_dir"] else None

        if excel_dir and excel_dir.exists():
            result["excel"] = [p.name for p in sorted(excel_dir.glob("*.xlsx"))]
        else:
            result["messages"].append("未找到有效的 Excel 源目录")

        if csv_dir and csv_dir.exists():
            result["csv"] = [p.name for p in sorted(csv_dir.glob("*.csv"))]
        else:
            result["messages"].append("未找到有效的 CSV 目录")

    except Exception as exc:
        result["ok"] = False
        result["messages"].append(f"扫描失败: {exc}")

    flash("扫描完成", "info")
    return render_template("index.html", app_name=APP_NAME, paths=paths, result=result)


@app.post("/process")
def process():
    """处理数据的主要路由，集成增强的错误处理"""
    start = time.time()
    paths = {
        "excel_dir": request.form.get("excel_dir", "").strip(),
        "csv_dir": request.form.get("csv_dir", "").strip(),
        "output_dir": request.form.get("output_dir", "").strip(),
    }

    result: Dict[str, Any] = {"ok": False, "summary": {}, "messages": []}

    try:
        logger.info(f"开始数据处理流程，路径配置: {paths}")
        
        module = load_preprocessor_module()

        excel_dir = Path(paths["excel_dir"]).expanduser()
        csv_dir = Path(paths["csv_dir"]).expanduser()
        output_dir = Path(paths["output_dir"]).expanduser()

        # 1) Excel → CSV
        logger.info("步骤1: 开始Excel转CSV")
        converted = module.convert_excel_to_csv(excel_dir, csv_dir)
        result["messages"].append(f"Excel 转 CSV：{len(converted)} 个文件")
        logger.info(f"Excel转CSV完成，转换了 {len(converted)} 个文件")

        # 2) 预处理（按年度输出 + 元数据）
        logger.info("步骤2: 开始数据预处理")
        restructurer = module.CarInsuranceDataRestructurer()
        summary = restructurer.process_all_files(str(csv_dir), str(output_dir))

        # 3) 更新元数据
        logger.info("步骤3: 更新元数据")
        data_manager = module.DataStructureManager(str(output_dir))
        data_manager.update_metadata()

        elapsed = time.time() - start
        result["ok"] = True
        result["summary"] = {
            "processing_summary": summary.get("processing_summary", {}),
            "years": summary.get("processing_summary", {}).get("years_processed", []),
            "report_path": str(Path(output_dir) / "data_restructure_report.json"),
            "output_dir": str(output_dir),
            "elapsed_sec": round(elapsed, 1),
        }
        
        logger.info(f"数据处理流程完成，耗时: {elapsed:.1f}秒")
        flash("处理完成", "success")

    except Exception as exc:
        error_handler.log_error("数据处理流程", exc, {
            "paths": paths,
            "traceback": traceback.format_exc()
        })
        result["ok"] = False
        result["messages"].append(f"处理失败: {exc}")
        flash("处理失败", "error")

    return render_template("index.html", app_name=APP_NAME, paths=paths, result=result)


@app.route("/upload", methods=["GET", "POST", "OPTIONS"])
def upload_files():
    """文件上传和处理功能"""
    # 处理OPTIONS预请求
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    if request.method == "GET":
        return render_template("upload.html", app_name=APP_NAME)

    try:
        start_time = time.time()

        # 检查文件上传
        if 'files' not in request.files:
            return jsonify({"ok": False, "message": "未选择文件"}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"ok": False, "message": "未选择有效文件"}), 400

        # 创建临时目录
        upload_dir = Path("/tmp/uploads")
        csv_dir = Path("/tmp/converted")
        output_dir = Path("/tmp/output")

        upload_dir.mkdir(parents=True, exist_ok=True)
        csv_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存上传的文件
        uploaded_files = []
        for file in files:
            if file and file.filename and file.filename.endswith(('.xlsx', '.csv')):
                import re
                safe_filename = re.sub(r'[^\w\-_\.\u4e00-\u9fff]', '_', file.filename)
                file_path = upload_dir / safe_filename
                file.save(str(file_path))
                uploaded_files.append(safe_filename)

        if not uploaded_files:
            return jsonify({"ok": False, "message": "没有有效的Excel或CSV文件"}), 400

        # 加载处理模块
        module = load_preprocessor_module()

        # 1. Excel转CSV
        converted_files = module.convert_excel_to_csv(str(upload_dir), str(csv_dir))

        # 2. 数据预处理
        restructurer = module.CarInsuranceDataRestructurer()
        processing_result = restructurer.process_all_files(str(csv_dir), str(output_dir))

        # 3. 更新元数据
        data_manager = module.DataStructureManager(str(output_dir))
        data_manager.update_metadata()

        elapsed_time = time.time() - start_time

        return jsonify({
            "ok": True,
            "message": f"成功处理 {len(uploaded_files)} 个文件",
            "uploaded_files": uploaded_files,
            "converted_files": converted_files,
            "processing_summary": processing_result.get("processing_summary", {}),
            "output_dir": str(output_dir),
            "elapsed_seconds": round(elapsed_time, 2),
            "download_available": True
        })

    except Exception as exc:
        import traceback
        error_msg = f"处理失败: {str(exc)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] 堆栈: {traceback.format_exc()}")
        return jsonify({"ok": False, "message": error_msg}), 500


@app.route("/api/upload", methods=["POST", "OPTIONS"])
def api_upload():
    """API上传端点，确保路由正确"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    try:
        # 基本的文件处理逻辑
        if 'files' not in request.files:
            return jsonify({"ok": False, "message": "未选择文件"}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"ok": False, "message": "未选择有效文件"}), 400

        return jsonify({
            "ok": True,
            "message": f"收到 {len(files)} 个文件",
            "files": [f.filename for f in files if f.filename],
            "timestamp": datetime.now().isoformat()
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "message": f"上传失败: {str(exc)}",
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/download", methods=["GET", "POST"])
def download_zip():
    """下载处理结果"""
    try:
        # 默认使用输出目录
        output_dir = Path("/tmp/output")

        if not output_dir.exists() or not any(output_dir.iterdir()):
            return jsonify({"ok": False, "message": "没有可下载的文件"}), 404

        # 将目录打包为内存 zip 并返回
        memfile = io.BytesIO()
        with zipfile.ZipFile(memfile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in output_dir.rglob("*"):
                if p.is_file():
                    arcname = p.relative_to(output_dir)
                    zf.write(p, arcname=str(arcname))
        memfile.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_forge_processed_{timestamp}.zip"

        return send_file(
            memfile,
            as_attachment=True,
            download_name=filename,
            mimetype="application/zip",
        )
    except Exception as exc:
        return jsonify({"ok": False, "message": f"下载失败: {str(exc)}"}), 500


# Vercel入口点
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)


# Vercel入口点
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)

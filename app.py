#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险变动成本明细分析 - 数据预处理器 (简化版)
严格按照处理规范.md执行数据转换和字段映射
"""

import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import zipfile
import tempfile

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB限制

# 目录配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class DataProcessor:
    """数据处理器 - 简化版"""
    
    def __init__(self):
        # 完整的26字段列表（严格按照输出模板.csv顺序）
        self.required_fields = [
            # 17个筛选维度字段
            'snapshot_date',           # 刷新时间
            'policy_start_year',       # 保险起期
            'business_type_category',  # 业务类型
            'chengdu_branch',          # 成都中支
            'third_level_organization', # 三级机构
            'customer_category_3',     # 客户类别3
            'insurance_type',          # 险种类
            'is_new_energy_vehicle',   # 是否新能源车1
            'coverage_type',           # 交三/主全
            'is_transferred_vehicle',  # 是否过户车
            'renewal_status',          # 续保情况
            'vehicle_insurance_grade', # 车险分等级
            'highway_risk_grade',      # 高速风险等级
            'large_truck_score',       # 大货车评分
            'small_truck_score',       # 小货车评分
            'terminal_source',         # 终端来源
            # 9个绝对值字段（按模板顺序）
            'signed_premium_yuan',                    # 签单保费
            'matured_premium_yuan',                   # 满期保费
            'policy_count',                           # 保单件数
            'claim_case_count',                       # 赔案件数
            'reported_claim_payment_yuan',            # 已报告赔款
            'expense_amount_yuan',                    # 费用金额
            'commercial_premium_before_discount_yuan', # 商业险折前保费
            'premium_plan_yuan',                      # 保费计划
            'marginal_contribution_amount_yuan',      # 满期边际贡献额
            'week_number'              # 周次
        ]
        
        # 17个筛选维度字段（保持原有定义用于处理逻辑）
        self.filtering_fields = [
            'snapshot_date',           # 刷新时间
            'policy_start_year',       # 保险起期
            'business_type_category',  # 业务类型
            'chengdu_branch',          # 成都中支
            'third_level_organization', # 三级机构
            'customer_category_3',     # 客户类别3
            'insurance_type',          # 险种类
            'coverage_type',           # 交三/主全
            'renewal_status',          # 续保情况
            'terminal_source',         # 终端来源
            'vehicle_insurance_grade', # 车险分等级
            'highway_risk_grade',      # 高速风险等级
            'large_truck_score',       # 大货车评分
            'small_truck_score',       # 小货车评分
            'is_new_energy_vehicle',   # 是否新能源车1
            'is_transferred_vehicle',  # 是否过户车
            'week_number'              # 周次
        ]
        
        # 9个绝对值字段（保持原有定义用于处理逻辑）
        self.absolute_fields = [
            'signed_premium_yuan',                    # 签单保费
            'matured_premium_yuan',                   # 满期保费
            'commercial_premium_before_discount_yuan', # 商业险折前保费
            'policy_count',                           # 保单件数
            'claim_case_count',                       # 赔案件数
            'reported_claim_payment_yuan',            # 已报告赔款
            'expense_amount_yuan',                    # 费用金额
            'premium_plan_yuan',                      # 保费计划
            'marginal_contribution_amount_yuan'       # 满期边际贡献额
        ]
        
        # 中文字段名到英文字段名的映射
        self.field_mapping = {
            '刷新时间': 'snapshot_date',
            '保险起期': 'policy_start_year',
            '业务类型分类': 'business_type_category',
            '成都中支': 'chengdu_branch',
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
        }
        
        # 布尔值映射
        self.boolean_map = {
            '是': True, '否': False,
            'Y': True, 'N': False,
            'true': True, 'false': False,
            True: True, False: False
        }

    def standardize_fields(self, df, original_filename=None):
        """标准化字段名和数据类型"""
        # 首先重命名中文列名为英文列名
        df_renamed = df.rename(columns=self.field_mapping)
        
        # 创建结果DataFrame，保留所有重命名后的字段
        result_df = df_renamed.copy()
        
        # 处理筛选维度字段的默认值
        for field in self.filtering_fields:
            if field not in result_df.columns:
                # 设置默认值
                if field in ['is_new_energy_vehicle', 'is_transferred_vehicle']:
                    result_df[field] = False
                elif field in ['policy_start_year', 'week_number']:
                    result_df[field] = 0
                else:
                    result_df[field] = ''
        
        # 处理布尔字段
        for bool_field in ['is_new_energy_vehicle', 'is_transferred_vehicle']:
            if bool_field in result_df.columns:
                result_df[bool_field] = result_df[bool_field].apply(lambda x: self.boolean_map.get(x, False))
        
        # 处理年份字段 - 从保险起期字段提取年份
        if 'policy_start_year' in result_df.columns:
            # 如果保险起期是日期格式，提取年份；如果已经是年份，直接使用
            def extract_year(value):
                if pd.isna(value):
                    return 0
                try:
                    # 尝试转换为日期时间格式
                    if isinstance(value, str):
                        # 处理各种日期格式
                        if '/' in value or '-' in value or '年' in value:
                            # 尝试解析日期
                            date_obj = pd.to_datetime(value, errors='coerce')
                            if pd.notna(date_obj):
                                return date_obj.year
                        # 如果是纯数字字符串，直接转换
                        return int(float(value))
                    elif isinstance(value, (int, float)):
                        # 如果是数值，判断是年份还是日期序列号
                        if value > 1900 and value < 2100:
                            return int(value)
                        else:
                            # 可能是Excel日期序列号，尝试转换
                            date_obj = pd.to_datetime(value, origin='1900-01-01', unit='D', errors='coerce')
                            if pd.notna(date_obj):
                                return date_obj.year
                    else:
                        # 其他类型，尝试转换为日期
                        date_obj = pd.to_datetime(value, errors='coerce')
                        if pd.notna(date_obj):
                            return date_obj.year
                    return 0
                except:
                    return 0
            
            result_df['policy_start_year'] = result_df['policy_start_year'].apply(extract_year)
        else:
            result_df['policy_start_year'] = 0
        
        # 从文件名提取周次
        week_number = 40  # 默认值
        if original_filename:
            import re
            week_match = re.search(r'第(\d+)周', original_filename)
            if week_match:
                week_number = int(week_match.group(1))
        
        result_df['week_number'] = week_number
        
        return result_df

    def calculate_absolute_fields(self, df):
        """计算9个绝对值字段"""
        # 复制DataFrame以避免修改原数据
        result_df = df.copy()
        
        # 1. 签单保费(元) = 跟单保费(万) * 10000
        if 'signed_premium_wan' in df.columns:
            signed_premium_series = pd.to_numeric(df['signed_premium_wan'], errors='coerce').fillna(0)
            result_df['signed_premium_yuan'] = signed_premium_series.astype(float) * 10000
        else:
            result_df['signed_premium_yuan'] = 0.0
        
        # 2. 满期保费(元) = 满期净保费(万) * 10000
        if 'matured_premium_wan' in df.columns:
            matured_premium_series = pd.to_numeric(df['matured_premium_wan'], errors='coerce').fillna(0)
            result_df['matured_premium_yuan'] = matured_premium_series.astype(float) * 10000
        else:
            result_df['matured_premium_yuan'] = 0.0
        
        # 3. 商业险折前保费(元) = 满期保费(元) / 商业险自主系数（避免除零）
        if 'commercial_autonomous_coefficient' in df.columns:
            coeff = pd.to_numeric(df['commercial_autonomous_coefficient'], errors='coerce').fillna(1.0)
            coeff = coeff.replace(0, 1.0)  # 避免除零
            result_df['commercial_premium_before_discount_yuan'] = result_df['matured_premium_yuan'] / coeff
        else:
            result_df['commercial_premium_before_discount_yuan'] = result_df['matured_premium_yuan']
        
        # 4. 保单数量 = 满期保费(元) / 单均保费（避免除零）
        if 'average_premium' in df.columns:
            avg_premium = pd.to_numeric(df['average_premium'], errors='coerce').fillna(1.0)
            avg_premium = avg_premium.replace(0, 1.0)  # 避免除零
            result_df['policy_count'] = (result_df['matured_premium_yuan'] / avg_premium).round().astype(int)
        else:
            result_df['policy_count'] = 1
        
        # 5. 出险案件数 = 案件数
        if 'claim_case_count' in df.columns:
            claim_count_series = pd.to_numeric(df['claim_case_count'], errors='coerce').fillna(0)
            result_df['claim_case_count'] = claim_count_series.astype(int)
        else:
            result_df['claim_case_count'] = 0
        
        # 6. 已报案赔付(元) = 总赔款(万) * 10000
        if 'total_claim_wan' in df.columns:
            total_claim_series = pd.to_numeric(df['total_claim_wan'], errors='coerce').fillna(0)
            result_df['reported_claim_payment_yuan'] = total_claim_series.astype(float) * 10000
        else:
            result_df['reported_claim_payment_yuan'] = 0.0
        
        # 7. 费用金额(元) = 签单保费(元) * 费用率 (修正：应使用签单保费而非满期保费)
        if 'expense_ratio' in df.columns:
            expense_ratio = pd.to_numeric(df['expense_ratio'], errors='coerce').fillna(0.0)
            result_df['expense_amount_yuan'] = result_df['signed_premium_yuan'] * expense_ratio
        else:
            result_df['expense_amount_yuan'] = 0.0
        
        # 8. 保费计划(元) = 满期保费(元) * 保费计划系数
        if 'premium_plan_coefficient' in df.columns:
            plan_coeff = pd.to_numeric(df['premium_plan_coefficient'], errors='coerce').fillna(1.0)
            result_df['premium_plan_yuan'] = result_df['matured_premium_yuan'] * plan_coeff
        else:
            # 如果没有保费计划系数，默认等于满期保费
            result_df['premium_plan_yuan'] = result_df['matured_premium_yuan']
        
        # 9. 边际贡献金额(元) = 满期保费(元) * (1 - 变动成本率)
        if 'variable_cost_ratio' in df.columns:
            variable_cost_ratio = pd.to_numeric(df['variable_cost_ratio'], errors='coerce').fillna(0.0)
            result_df['marginal_contribution_amount_yuan'] = result_df['matured_premium_yuan'] * (1 - variable_cost_ratio)
        else:
            result_df['marginal_contribution_amount_yuan'] = result_df['matured_premium_yuan']
        
        return result_df

    def finalize_output(self, df):
        """最终输出处理，确保字段顺序和数量正确"""
        try:
            # 确保所有必需字段都存在
            output_df = pd.DataFrame()
            
            for field in self.required_fields:
                if field in df.columns:
                    output_df[field] = df[field]
                else:
                    logger.warning(f"缺少字段: {field}")
                    output_df[field] = None
            
            logger.info(f"最终输出字段: {list(output_df.columns)}")
            return output_df
            
        except Exception as e:
            logger.error(f"最终输出处理出错: {str(e)}")
            raise

    def create_zip_package(self, output_files, original_filename=None):
        """
        创建包含所有CSV文件的ZIP压缩包
        """
        try:
            # 从原始文件名提取周次信息
            week_number = 40  # 默认值
            if original_filename:
                import re
                week_match = re.search(r'第(\d+)周', original_filename)
                if week_match:
                    week_number = int(week_match.group(1))
            
            # 生成ZIP文件名
            if len(output_files) > 1:
                years = [file_info['year'] for file_info in output_files]
                year_range = f"{min(years)}-{max(years)}"
                zip_filename = f"{year_range}保单第{week_number:02d}周变动成本明细表.zip"
            else:
                year = output_files[0]['year']
                zip_filename = f"{year}保单第{week_number:02d}周变动成本明细表.zip"
            
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            
            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in output_files:
                    csv_path = file_info['path']
                    csv_filename = file_info['filename']
                    
                    if os.path.exists(csv_path):
                        # 将CSV文件添加到ZIP中
                        zipf.write(csv_path, csv_filename)
                        logger.info(f"已添加文件到ZIP: {csv_filename}")
                    else:
                        logger.warning(f"CSV文件不存在: {csv_path}")
            
            logger.info(f"ZIP文件创建成功: {zip_path}")
            
            return {
                'success': True,
                'filename': zip_filename,  # 修改为filename以保持一致性
                'zip_path': zip_path,
                'file_count': len(output_files)
            }
            
        except Exception as e:
            logger.error(f"创建ZIP文件时出错: {str(e)}")
            return {
                'success': False,
                'message': f'创建ZIP文件失败: {str(e)}'
            }

    def generate_output_filename(self, df, original_filename):
        """
        根据数据内容生成输出文件名
        格式: YYYY保单第WW周变动成本明细表.csv 或 YYYY-YYYY保单第WW周变动成本明细表.csv（多年度）
        """
        try:
            # 获取保单年度
            if 'policy_start_year' in df.columns:
                years = df['policy_start_year'].dropna().unique()
                years = sorted([int(year) for year in years if pd.notna(year)])
            else:
                # 如果没有policy_start_year字段，尝试从原始文件名提取
                import re
                year_match = re.search(r'第(\d+)周', original_filename)
                if year_match:
                    # 假设当前年份
                    years = [datetime.now().year]
                else:
                    years = [2024]  # 默认年份
            
            # 获取周数
            if 'week_number' in df.columns:
                weeks = df['week_number'].dropna().unique()
                week = int(weeks[0]) if len(weeks) > 0 else 40
            else:
                # 尝试从原始文件名提取周数
                import re
                week_match = re.search(r'第(\d+)周', original_filename)
                week = int(week_match.group(1)) if week_match else 40
            
            # 生成文件名
            if len(years) == 1:
                filename = f"{years[0]}保单第{week:02d}周变动成本明细表.csv"
            else:
                year_range = f"{min(years)}-{max(years)}"
                filename = f"{year_range}保单第{week:02d}周变动成本明细表.csv"
            
            logger.info(f"生成文件名: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"生成文件名时出错: {str(e)}")
            # 返回默认文件名
            return f"保单第40周变动成本明细表.csv"

    def process_excel_to_csv(self, excel_path, output_path=None, original_filename=None):
        """处理Excel文件转换为CSV，按年度分组输出多个文件"""
        try:
            # 读取Excel文件
            logger.info(f"读取Excel文件: {excel_path}")
            df = pd.read_excel(excel_path)
            logger.info(f"原始数据: {len(df)} 行, {len(df.columns)} 列")
            
            # 标准化字段
            df_standardized = self.standardize_fields(df, original_filename)
            logger.info(f"标准化后: {len(df_standardized)} 行, {len(df_standardized.columns)} 列")
            
            # 计算绝对值字段
            df_with_absolute = self.calculate_absolute_fields(df_standardized)
            logger.info(f"计算绝对值字段后: {len(df_with_absolute)} 行, {len(df_with_absolute.columns)} 列")
            
            # 最终输出处理
            df_final = self.finalize_output(df_with_absolute)
            logger.info(f"最终输出: {len(df_final)} 行, {len(df_final.columns)} 列")
            
            # 按年度分组数据
            if 'policy_start_year' not in df_final.columns:
                logger.error("缺少policy_start_year字段，无法按年度分组")
                return {
                    'success': False,
                    'message': '缺少保单年度字段，无法按年度分组输出'
                }
            
            # 获取所有年度
            years = df_final['policy_start_year'].dropna().unique()
            years = sorted([int(year) for year in years if pd.notna(year)])
            logger.info(f"发现年度: {years}")
            
            # 获取周数（用于文件命名）
            week_number = 40  # 默认值
            if 'week_number' in df_final.columns:
                weeks = df_final['week_number'].dropna().unique()
                if len(weeks) > 0:
                    week_number = int(weeks[0])
            else:
                # 尝试从原始文件名提取周数
                import re
                week_match = re.search(r'第(\d+)周', original_filename or excel_path)
                if week_match:
                    week_number = int(week_match.group(1))
            
            # 为每个年度生成单独的文件
            output_files = []
            total_rows = 0
            
            for year in years:
                # 筛选当前年度的数据
                year_data = df_final[df_final['policy_start_year'] == year].copy()
                
                if len(year_data) == 0:
                    logger.warning(f"{year}年度没有数据")
                    continue
                
                # 生成文件名
                output_filename = f"{year}保单第{week_number:02d}周变动成本明细表.csv"
                year_output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                # 验证字段数量
                if len(year_data.columns) != 26:
                    logger.warning(f"{year}年度字段数量不符合规范: 期望26个，实际{len(year_data.columns)}个")
                
                # 保存CSV文件
                year_data.to_csv(year_output_path, index=False, encoding='utf-8-sig')
                logger.info(f"{year}年度CSV文件已保存: {year_output_path} ({len(year_data)}行)")
                
                output_files.append({
                    'year': year,
                    'filename': output_filename,
                    'path': year_output_path,
                    'row_count': len(year_data)
                })
                total_rows += len(year_data)
            
            if not output_files:
                return {
                    'success': False,
                    'message': '没有有效的年度数据可以输出'
                }

            # 创建ZIP压缩包
            zip_result = self.create_zip_package(output_files, original_filename)
            
            return {
                'success': True,
                'message': f'成功处理 {total_rows} 行数据，按年度输出 {len(output_files)} 个文件',
                'output_files': output_files,
                'field_count': len(df_final.columns),
                'total_row_count': total_rows,
                'years_processed': years,
                'zip_info': zip_result
            }
            
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
            return {
                'success': False,
                'message': f'处理失败: {str(e)}'
            }

# 创建处理器实例
processor = DataProcessor()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传和处理"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': '请上传Excel文件'})
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
        file.save(upload_path)
        
        # 处理文件
        result = processor.process_excel_to_csv(upload_path, None, filename)
        
        if result['success']:
            # 只添加ZIP文件下载链接，移除单独文件下载逻辑
            if 'zip_info' in result and result['zip_info']['success']:
                result['zip_download_url'] = f'/download/{result["zip_info"]["filename"]}'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"上传处理出错: {str(e)}")
        return jsonify({'success': False, 'message': f'处理失败: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    """文件下载"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件出错: {str(e)}")
        return jsonify({'error': '下载失败'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
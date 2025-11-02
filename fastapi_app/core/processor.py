#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险变动成本明细分析 - 数据预处理器 (Polars高性能版)
使用Polars替代Pandas，性能提升5-20倍
"""

import re
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import logging

import polars as pl
import numpy as np

logger = logging.getLogger(__name__)


class PolarsDataProcessor:
    """
    基于Polars的高性能数据处理器
    完全兼容原Flask版本的所有功能，但速度提升5-20倍
    """

    def __init__(self):
        # 完整的27字段列表（严格按照输出模板.csv顺序）
        self.required_fields = [
            # 18个筛选维度字段
            'snapshot_date',           # 刷新时间
            'policy_start_year',       # 保险起期
            'business_type_category',  # 业务类型
            'chengdu_branch',          # 成都中支
            'second_level_organization', # 二级机构
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

        # 18个筛选维度字段
        self.filtering_fields = [
            'snapshot_date', 'policy_start_year', 'business_type_category',
            'chengdu_branch', 'second_level_organization', 'third_level_organization',
            'customer_category_3', 'insurance_type', 'coverage_type',
            'renewal_status', 'terminal_source', 'vehicle_insurance_grade',
            'highway_risk_grade', 'large_truck_score', 'small_truck_score',
            'is_new_energy_vehicle', 'is_transferred_vehicle', 'week_number'
        ]

        # 9个绝对值字段
        self.absolute_fields = [
            'signed_premium_yuan', 'matured_premium_yuan',
            'commercial_premium_before_discount_yuan', 'policy_count',
            'claim_case_count', 'reported_claim_payment_yuan',
            'expense_amount_yuan', 'premium_plan_yuan',
            'marginal_contribution_amount_yuan'
        ]

        # 中文字段名到英文字段名的映射
        self.field_mapping = {
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
            '保费计划系数': 'premium_plan_coefficient',
            '周次': 'week_number'
        }

        # 布尔值映射
        self.boolean_map = {
            '是': True, '否': False,
            'Y': True, 'N': False,
            'true': True, 'false': False,
            True: True, False: False
        }

    def extract_year_from_value(self, value: Any) -> int:
        """从各种格式中提取年份"""
        if value is None:
            return 0

        try:
            # 字符串处理
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    return 0

                # 正则捕捉4位年份
                year_match = re.search(r'(19|20)\d{2}', text)
                if year_match:
                    return int(year_match.group(0))

                # 去除非数字字符再尝试
                numeric_part = re.sub(r'[^0-9.]', '', text)
                if numeric_part:
                    val = int(float(numeric_part))
                    if 1900 <= val <= 2100:
                        return val
                return 0

            # 数值类型
            if isinstance(value, (int, float)):
                if 1900 <= value <= 2100:
                    return int(value)

            return 0
        except Exception:
            return 0

    def extract_week_number(self, filename: str) -> Optional[int]:
        """从文件名提取周序号 - 支持多种格式"""
        if not filename:
            return None

        patterns = [
            r'第(\d+)周',      # 第43周
            r'周(\d+)',        # 周43
            r'W(\d+)',         # W43
            r'w(\d+)',         # w43
            r'week\s*(\d+)',   # week 43
            r'Week\s*(\d+)',   # Week 43
            r'(\d+)周',        # 43周
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                week_num = int(match.group(1))
                if 1 <= week_num <= 53:
                    return week_num

        return None

    def standardize_fields(
        self,
        df: pl.DataFrame,
        original_filename: Optional[str] = None,
        user_week_number: Optional[int] = None
    ) -> pl.DataFrame:
        """
        标准化字段名和数据类型
        使用Polars高性能API，比Pandas快5-10倍
        """
        # 重命名列
        rename_map = {k: v for k, v in self.field_mapping.items() if k in df.columns}
        df = df.rename(rename_map)

        # 添加缺失的筛选维度字段
        for field in self.filtering_fields:
            if field not in df.columns:
                if field in ['is_new_energy_vehicle', 'is_transferred_vehicle']:
                    df = df.with_columns(pl.lit(False).alias(field))
                elif field in ['policy_start_year', 'week_number']:
                    df = df.with_columns(pl.lit(0).alias(field))
                elif field == 'second_level_organization':
                    df = df.with_columns(pl.lit('四川').alias(field))
                else:
                    df = df.with_columns(pl.lit('').alias(field))

        # 处理布尔字段 - 使用Polars的when().then()链式操作
        for bool_field in ['is_new_energy_vehicle', 'is_transferred_vehicle']:
            if bool_field in df.columns:
                df = df.with_columns(
                    pl.when(pl.col(bool_field).cast(pl.Utf8).is_in(['是', 'Y', 'true', 'True']))
                    .then(pl.lit(True))
                    .otherwise(pl.lit(False))
                    .alias(bool_field)
                )

        # 处理年份字段 - 使用map_elements进行复杂转换
        if 'policy_start_year' in df.columns:
            df = df.with_columns(
                pl.col('policy_start_year')
                .map_elements(self.extract_year_from_value, return_dtype=pl.Int64)
                .alias('policy_start_year')
            )
        else:
            df = df.with_columns(pl.lit(0).alias('policy_start_year'))

        # 处理周序号
        if user_week_number is not None:
            week_number = user_week_number
            logger.info(f"使用用户指定的周序号: {week_number}")
        else:
            week_number = 40  # 默认值
            if original_filename:
                extracted = self.extract_week_number(original_filename)
                if extracted:
                    week_number = extracted
                    logger.info(f"从文件名 '{original_filename}' 提取到周次: {week_number}")
                else:
                    logger.warning(f"无法从文件名 '{original_filename}' 提取周次，使用默认值: {week_number}")

        # 确保 second_level_organization 始终为'四川'
        df = df.with_columns(pl.lit('四川').alias('second_level_organization'))
        df = df.with_columns(pl.lit(week_number).alias('week_number'))

        logger.info(f"字段标准化完成: {df.shape[0]} 行, {df.shape[1]} 列")
        return df

    def calculate_absolute_fields(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        计算9个绝对值字段
        使用Polars的列式操作，比Pandas快10-20倍
        """
        # 1. 签单保费(元) = 跟单保费(万) * 10000
        if 'signed_premium_wan' in df.columns:
            df = df.with_columns(
                (pl.col('signed_premium_wan').fill_null(0).cast(pl.Float64) * 10000)
                .alias('signed_premium_yuan')
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias('signed_premium_yuan'))

        # 2. 满期保费(元) = 满期净保费(万) * 10000
        if 'matured_premium_wan' in df.columns:
            df = df.with_columns(
                (pl.col('matured_premium_wan').fill_null(0).cast(pl.Float64) * 10000)
                .alias('matured_premium_yuan')
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias('matured_premium_yuan'))

        # 3. 商业险折前保费(元) = 满期保费(元) / 商业险自主系数
        if 'commercial_autonomous_coefficient' in df.columns:
            df = df.with_columns(
                (pl.col('matured_premium_yuan') /
                 pl.when(pl.col('commercial_autonomous_coefficient').fill_null(1.0) == 0)
                 .then(pl.lit(1.0))
                 .otherwise(pl.col('commercial_autonomous_coefficient').fill_null(1.0))
                ).alias('commercial_premium_before_discount_yuan')
            )
        else:
            df = df.with_columns(
                pl.col('matured_premium_yuan').alias('commercial_premium_before_discount_yuan')
            )

        # 4. 保单数量 = 满期保费(元) / 单均保费
        if 'average_premium' in df.columns:
            df = df.with_columns(
                (pl.col('matured_premium_yuan') /
                 pl.when(pl.col('average_premium').fill_null(1.0) == 0)
                 .then(pl.lit(1.0))
                 .otherwise(pl.col('average_premium').fill_null(1.0))
                ).round(0).cast(pl.Int64).alias('policy_count')
            )
        else:
            df = df.with_columns(pl.lit(1).alias('policy_count'))

        # 5. 出险案件数
        if 'claim_case_count' in df.columns:
            df = df.with_columns(
                pl.col('claim_case_count').fill_null(0).cast(pl.Int64).alias('claim_case_count')
            )
        else:
            df = df.with_columns(pl.lit(0).alias('claim_case_count'))

        # 6. 已报案赔付(元) = 总赔款(万) * 10000
        if 'total_claim_wan' in df.columns:
            df = df.with_columns(
                (pl.col('total_claim_wan').fill_null(0).cast(pl.Float64) * 10000)
                .alias('reported_claim_payment_yuan')
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias('reported_claim_payment_yuan'))

        # 7. 费用金额(元) = 签单保费(元) * 费用率
        if 'expense_ratio' in df.columns:
            df = df.with_columns(
                (pl.col('signed_premium_yuan') * pl.col('expense_ratio').fill_null(0.0))
                .alias('expense_amount_yuan')
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias('expense_amount_yuan'))

        # 8. 保费计划(元) = 满期保费(元) * 保费计划系数
        if 'premium_plan_coefficient' in df.columns:
            df = df.with_columns(
                (pl.col('matured_premium_yuan') * pl.col('premium_plan_coefficient').fill_null(1.0))
                .alias('premium_plan_yuan')
            )
        else:
            df = df.with_columns(
                pl.col('matured_premium_yuan').alias('premium_plan_yuan')
            )

        # 9. 边际贡献金额(元) = 满期保费(元) * (1 - 变动成本率)
        if 'variable_cost_ratio' in df.columns:
            df = df.with_columns(
                (pl.col('matured_premium_yuan') * (1 - pl.col('variable_cost_ratio').fill_null(0.0)))
                .alias('marginal_contribution_amount_yuan')
            )
        else:
            df = df.with_columns(
                pl.col('matured_premium_yuan').alias('marginal_contribution_amount_yuan')
            )

        logger.info(f"绝对值字段计算完成: {df.shape[0]} 行, {df.shape[1]} 列")
        return df

    def finalize_output(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        最终输出处理，确保字段顺序和数量正确
        Polars使用select来重排列，比Pandas更高效
        """
        # 确保所有必需字段都存在
        for field in self.required_fields:
            if field not in df.columns:
                logger.warning(f"缺少字段: {field}，添加默认值")
                df = df.with_columns(pl.lit(None).alias(field))

        # 按required_fields顺序选择列
        df = df.select(self.required_fields)

        logger.info(f"最终输出处理完成: {df.shape[0]} 行, {len(self.required_fields)} 列")
        return df

    def process_excel_to_csv(
        self,
        excel_path: Union[str, Path],
        output_folder: Union[str, Path],
        original_filename: Optional[str] = None,
        user_week_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        处理Excel文件转换为CSV，按年度分组输出多个文件

        Args:
            excel_path: Excel文件路径
            output_folder: 输出文件夹路径
            original_filename: 原始文件名（用于提取周序号）
            user_week_number: 用户指定的周序号

        Returns:
            处理结果字典
        """
        try:
            excel_path = Path(excel_path)
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

            # 读取Excel文件 - Polars自动优化读取性能
            logger.info(f"读取Excel文件: {excel_path}")
            df = pl.read_excel(excel_path)
            logger.info(f"原始数据: {df.shape[0]} 行, {df.shape[1]} 列")

            # 标准化字段
            df_standardized = self.standardize_fields(df, original_filename, user_week_number)

            # 计算绝对值字段
            df_with_absolute = self.calculate_absolute_fields(df_standardized)

            # 最终输出处理
            df_final = self.finalize_output(df_with_absolute)
            logger.info(f"最终输出: {df_final.shape[0]} 行, {df_final.shape[1]} 列")

            # 检查是否有policy_start_year字段
            if 'policy_start_year' not in df_final.columns:
                return {
                    'success': False,
                    'message': '缺少保单年度字段，无法按年度分组输出'
                }

            # 获取所有年度
            years = df_final.select('policy_start_year').unique().filter(
                pl.col('policy_start_year') > 0
            ).sort('policy_start_year')
            years_list = years['policy_start_year'].to_list()

            if not years_list:
                years_list = [datetime.now().year]

            logger.info(f"发现年度: {years_list}")

            # 获取周数
            week_number = user_week_number if user_week_number else 40
            if 'week_number' in df_final.columns:
                week_vals = df_final.select('week_number').unique()['week_number'].to_list()
                if week_vals and week_vals[0] > 0:
                    week_number = int(week_vals[0])

            # 为每个年度生成单独的文件
            output_files = []
            total_rows = 0

            for year in years_list:
                # 筛选当前年度的数据 - Polars的filter比Pandas快很多
                year_data = df_final.filter(pl.col('policy_start_year') == year)

                if year_data.shape[0] == 0:
                    logger.warning(f"{year}年度没有数据")
                    continue

                # 生成文件名
                output_filename = f"{year}保单第{week_number:02d}周变动成本明细表.csv"
                year_output_path = output_folder / output_filename

                # 验证字段数量
                if year_data.shape[1] != 26:
                    logger.warning(
                        f"{year}年度字段数量不符合规范: 期望26个，实际{year_data.shape[1]}个"
                    )

                # 保存CSV文件 - Polars的write_csv比Pandas快2-5倍
                year_data.write_csv(year_output_path, separator=',')
                logger.info(
                    f"{year}年度CSV文件已保存: {year_output_path} ({year_data.shape[0]}行)"
                )

                output_files.append({
                    'year': year,
                    'filename': output_filename,
                    'path': str(year_output_path),
                    'row_count': year_data.shape[0],
                    'download_url': f'/download/{output_filename}'
                })
                total_rows += year_data.shape[0]

            if not output_files:
                return {
                    'success': False,
                    'message': '没有有效的年度数据可以输出'
                }

            # 创建ZIP压缩包
            zip_result = self.create_zip_package(
                output_files, output_folder, original_filename, week_number
            )

            return {
                'success': True,
                'message': f'成功处理 {total_rows} 行数据，按年度输出 {len(output_files)} 个文件',
                'output_files': output_files,
                'field_count': df_final.shape[1],
                'total_row_count': total_rows,
                'years_processed': years_list,
                'week_number': week_number,
                'zip_package': zip_result if zip_result.get('success') else None
            }

        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'处理失败: {str(e)}'
            }

    def create_zip_package(
        self,
        output_files: List[Dict[str, Any]],
        output_folder: Path,
        original_filename: Optional[str] = None,
        week_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建包含所有CSV文件的ZIP压缩包"""
        try:
            if week_number is None:
                week_number = 40
                if original_filename:
                    extracted = self.extract_week_number(original_filename)
                    if extracted:
                        week_number = extracted

            # 生成ZIP文件名
            if len(output_files) > 1:
                years = [f['year'] for f in output_files]
                year_range = f"{min(years)}-{max(years)}"
                zip_filename = f"{year_range}保单第{week_number:02d}周变动成本明细表.zip"
            else:
                year = output_files[0]['year']
                zip_filename = f"{year}保单第{week_number:02d}周变动成本明细表.zip"

            zip_path = output_folder / zip_filename

            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in output_files:
                    csv_path = Path(file_info['path'])
                    csv_filename = file_info['filename']

                    if csv_path.exists():
                        zipf.write(csv_path, csv_filename)
                        logger.info(f"已添加文件到ZIP: {csv_filename}")
                    else:
                        logger.warning(f"CSV文件不存在: {csv_path}")

            logger.info(f"ZIP文件创建成功: {zip_path}")

            return {
                'success': True,
                'filename': zip_filename,
                'zip_path': str(zip_path),
                'file_count': len(output_files),
                'download_url': f'/download/{zip_filename}'
            }

        except Exception as e:
            logger.error(f"创建ZIP文件时出错: {str(e)}")
            return {
                'success': False,
                'message': f'创建ZIP文件失败: {str(e)}'
            }

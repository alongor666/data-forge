#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险变动成本明细分析 - FastAPI高性能版本
使用FastAPI + Polars，性能提升10-30倍
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .core.processor import PolarsDataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Database预处理 - 高性能版",
    description="车险变动成本明细分析数据预处理器 (FastAPI + Polars)",
    version="3.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件的目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 目录配置
IS_VERCEL = os.environ.get('VERCEL_ENV') == 'production'

if IS_VERCEL:
    # Vercel环境使用系统临时目录
    temp_dir = Path(tempfile.gettempdir())
    UPLOAD_FOLDER = temp_dir / 'uploads'
    OUTPUT_FOLDER = temp_dir / '处理后'
else:
    # 本地环境使用项目根目录
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / '处理后'

# 创建必要的目录
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

logger.info(f"运行环境: {'Vercel Serverless' if IS_VERCEL else '本地开发'}")
logger.info(f"上传目录: {UPLOAD_FOLDER}")
logger.info(f"输出目录: {OUTPUT_FOLDER}")

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 模板配置
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 创建数据处理器实例
processor = PolarsDataProcessor()

# 配置常量
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILES = 10
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}


# Pydantic模型
class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: str
    version: str
    environment: str


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool
    message: str
    files: List[dict] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)


@app.get("/", response_class=FileResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "Database预处理"
    })


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="3.0.0",
        environment="vercel" if IS_VERCEL else "local"
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_files(
    request: Request,
    file: List[UploadFile] = File(..., alias="file"),
    week_numbers: List[str] = Form(default=[]),
    client_ids: List[str] = Form(default=[]),
    week_number: Optional[str] = Form(default=None)
):
    """
    文件上传和处理端点

    支持：
    - 多文件批量上传
    - 每个文件独立周序号
    - 向后兼容统一周序号
    """
    try:
        # 验证文件数量
        if len(file) > MAX_FILES:
            raise HTTPException(
                status_code=400,
                detail=f'文件数量超限！最多允许 {MAX_FILES} 个文件，当前上传了 {len(file)} 个文件'
            )

        # 处理周序号列表
        if not week_numbers:
            # 兼容旧版本：使用统一的week_number
            if week_number:
                try:
                    unified_week = int(week_number)
                    if not (1 <= unified_week <= 53):
                        raise HTTPException(
                            status_code=400,
                            detail='周序号必须在1-53之间'
                        )
                    week_numbers = [str(unified_week)] * len(file)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail='周序号必须是有效数字'
                    )
            else:
                week_numbers = []

        # 验证周序号列表长度
        if week_numbers and len(week_numbers) != len(file):
            raise HTTPException(
                status_code=400,
                detail=f'周序号数量({len(week_numbers)})与文件数量({len(file)})不匹配'
            )

        processed_entries = []
        aggregated_years = set()
        total_rows = 0
        success_count = 0
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for index, upload_file in enumerate(file):
            original_filename = upload_file.filename
            client_reference = client_ids[index] if index < len(client_ids) else None

            # 获取该文件的周序号
            file_week_number = None
            if index < len(week_numbers):
                try:
                    file_week_number = int(week_numbers[index])
                    if not (1 <= file_week_number <= 53):
                        processed_entries.append({
                            'queue_index': index,
                            'client_id': client_reference,
                            'original_filename': original_filename,
                            'status': 'failed',
                            'message': f'周序号 {file_week_number} 无效,必须在1-53之间'
                        })
                        continue
                except ValueError:
                    processed_entries.append({
                        'queue_index': index,
                        'client_id': client_reference,
                        'original_filename': original_filename,
                        'status': 'failed',
                        'message': f'周序号格式错误: {week_numbers[index]}'
                    })
                    continue

            # 验证文件扩展名
            file_ext = Path(original_filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                processed_entries.append({
                    'queue_index': index,
                    'client_id': client_reference,
                    'original_filename': original_filename,
                    'status': 'unsupported',
                    'message': '仅支持Excel文件 (.xlsx / .xls)'
                })
                continue

            # 验证文件大小
            content = await upload_file.read()
            if len(content) > MAX_FILE_SIZE:
                processed_entries.append({
                    'queue_index': index,
                    'client_id': client_reference,
                    'original_filename': original_filename,
                    'status': 'failed',
                    'message': f'文件大小超限 ({len(content) / 1024 / 1024:.1f}MB > {MAX_FILE_SIZE / 1024 / 1024}MB)'
                })
                continue

            # 保存上传的文件
            safe_filename = f"{timestamp}_{index:02d}_{original_filename}"
            upload_path = UPLOAD_FOLDER / safe_filename

            with open(upload_path, 'wb') as f:
                f.write(content)

            # 处理文件
            logger.info(f"开始处理文件: {original_filename}, 周序号: {file_week_number}")
            result = processor.process_excel_to_csv(
                excel_path=upload_path,
                output_folder=OUTPUT_FOLDER,
                original_filename=original_filename,
                user_week_number=file_week_number
            )

            # 构建响应条目
            entry = {
                'queue_index': index,
                'client_id': client_reference,
                'original_filename': original_filename,
                'saved_as': safe_filename,
                'status': 'success' if result.get('success') else 'failed',
                'message': result.get('message'),
                'outputs': result.get('output_files', []),
                'total_row_count': result.get('total_row_count', 0),
                'field_count': result.get('field_count', 0),
                'years_processed': result.get('years_processed', []),
                'week_number': result.get('week_number'),
                'zip_package': result.get('zip_package'),
                'uploaded_at': timestamp
            }

            if result.get('success'):
                success_count += 1
                total_rows += result.get('total_row_count', 0)
                aggregated_years.update(entry['years_processed'])
            else:
                entry['error'] = result.get('message')

            processed_entries.append(entry)

            # 清理临时上传文件
            try:
                upload_path.unlink()
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")

        # 构建汇总信息
        failed_count = len(processed_entries) - success_count
        overall_success = success_count > 0 and failed_count == 0

        # 收集所有使用的周序号
        week_numbers_used = set()
        for entry in processed_entries:
            week_num = entry.get('week_number')
            if week_num:
                week_numbers_used.add(week_num)

        # 显示周序号摘要
        summary_week_display = None
        if week_numbers_used:
            sorted_weeks = sorted(week_numbers_used)
            if len(sorted_weeks) == 1:
                summary_week_display = sorted_weeks[0]
            else:
                summary_week_display = f"{min(sorted_weeks)}-{max(sorted_weeks)}"

        return UploadResponse(
            success=overall_success,
            message=f"成功处理 {success_count} / {len(processed_entries)} 个文件" if processed_entries else '未处理任何文件',
            files=processed_entries,
            summary={
                'total_files': len(processed_entries),
                'successful': success_count,
                'failed': failed_count,
                'total_row_count': total_rows,
                'years': sorted([int(y) for y in aggregated_years if y and int(y) > 0]),
                'week_number': summary_week_display,
                'week_numbers_used': sorted(week_numbers_used),
                'generated_at': timestamp
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传处理出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f'处理失败: {str(e)}')


@app.get("/download/{filename}")
async def download_file(filename: str):
    """文件下载端点"""
    try:
        file_path = OUTPUT_FOLDER / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail='文件不存在')

        # 验证文件路径安全性（防止路径遍历攻击）
        if not file_path.resolve().is_relative_to(OUTPUT_FOLDER.resolve()):
            raise HTTPException(status_code=403, detail='非法文件路径')

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='下载失败')


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"服务器内部错误: {str(exc)}"
        }
    )


# 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 FastAPI应用启动成功")
    logger.info(f"📁 上传目录: {UPLOAD_FOLDER}")
    logger.info(f"📁 输出目录: {OUTPUT_FOLDER}")
    logger.info(f"⚡ 使用Polars高性能数据处理引擎")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 FastAPI应用关闭")


def main():
    """主函数 - 用于本地开发"""
    port = int(os.environ.get('PORT', 5001))

    logger.info(f"🌐 启动服务器: http://127.0.0.1:{port}")
    logger.info(f"📚 API文档: http://127.0.0.1:{port}/docs")
    logger.info(f"📖 交互式API: http://127.0.0.1:{port}/redoc")

    uvicorn.run(
        "fastapi_app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not IS_VERCEL,  # 本地环境启用热重载
        log_level="info"
    )


if __name__ == "__main__":
    main()

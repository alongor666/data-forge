#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
import json
import time
import zipfile
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from flask import Flask, render_template, request, send_file, redirect, url_for, flash


APP_NAME = "数据预处理器"

app = Flask(__name__)
app.secret_key = os.environ.get("DATA_PREPROCESSOR_SECRET", "dev-secret")


@app.template_filter('strftime')
def strftime_filter(format_string):
    """自定义 Jinja2 过滤器：格式化当前时间"""
    return datetime.now().strftime(format_string)


def load_preprocessor_module():
    """动态加载数据预处理模块，如果不存在则使用内置模拟功能"""
    import importlib.util

    # 尝试加载外部脚本
    project_root = Path(__file__).resolve().parent.parent
    script_path = project_root / "数据转换" / "数据预处理脚本.py"

    if script_path.exists():
        spec = importlib.util.spec_from_file_location("data_preprocessor", str(script_path))
        module = importlib.util.module_from_spec(spec)  # type: ignore
        if spec and spec.loader:
            spec.loader.exec_module(module)  # type: ignore
            return module

    # 使用内置模拟功能
    return create_mock_preprocessor()


def create_mock_preprocessor():
    """创建模拟数据处理模块，用于云端部署演示"""
    import types
    import csv
    import pandas as pd

    module = types.ModuleType("mock_preprocessor")

    def convert_excel_to_csv(excel_dir, csv_dir):
        """模拟Excel到CSV转换功能"""
        excel_dir = Path(excel_dir)
        csv_dir = Path(csv_dir)
        csv_dir.mkdir(parents=True, exist_ok=True)

        converted = []
        try:
            import pandas as pd
            for excel_file in excel_dir.glob("*.xlsx"):
                try:
                    # 读取Excel文件
                    df = pd.read_excel(excel_file)
                    # 保存为CSV
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
                    writer.writerow(['模拟数据列1', '模拟数据列2', '处理时间'])
                    writer.writerow(['示例值1', '示例值2', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                converted.append(excel_file.name)

        return converted

    class CarInsuranceDataRestructurer:
        def process_all_files(self, csv_dir, output_dir):
            """模拟数据预处理功能"""
            csv_dir = Path(csv_dir)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            processed_files = 0
            failed_files = 0
            years_processed = []

            for csv_file in csv_dir.glob("*.csv"):
                try:
                    # 模拟处理：复制文件到输出目录
                    output_file = output_dir / f"processed_{csv_file.name}"

                    try:
                        import pandas as pd
                        # 使用pandas处理
                        df = pd.read_csv(csv_file)
                        # 添加处理时间戳
                        df['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    except ImportError:
                        # 简单复制
                        import shutil
                        shutil.copy2(csv_file, output_file)

                    processed_files += 1
                    current_year = datetime.now().year
                    if current_year not in years_processed:
                        years_processed.append(current_year)

                except Exception as e:
                    print(f"处理失败 {csv_file.name}: {e}")
                    failed_files += 1

            # 创建处理报告
            report_file = output_dir / "data_restructure_report.json"
            report = {
                "timestamp": datetime.now().isoformat(),
                "processing_summary": {
                    "successful": processed_files,
                    "failed": failed_files,
                    "years_processed": years_processed
                },
                "files_processed": processed_files,
                "output_directory": str(output_dir)
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return {
                "processing_summary": {
                    "successful": processed_files,
                    "failed": failed_files,
                    "years_processed": years_processed
                }
            }

    class DataStructureManager:
        def __init__(self, output_dir):
            self.output_dir = Path(output_dir)

        def update_metadata(self):
            """模拟元数据更新"""
            metadata_file = self.output_dir / "metadata.json"
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "file_count": len(list(self.output_dir.glob("*.csv"))),
                "processor": "Data Forge Cloud",
                "version": "1.0.0"
            }

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 将函数和类添加到模块
    module.convert_excel_to_csv = convert_excel_to_csv
    module.CarInsuranceDataRestructurer = CarInsuranceDataRestructurer
    module.DataStructureManager = DataStructureManager

    return module


def default_paths() -> Dict[str, str]:
    # 云端部署时使用临时目录
    if os.environ.get("VERCEL") or os.environ.get("TMPDIR"):
        temp_dir = Path("/tmp/claude") if os.environ.get("TMPDIR") else Path("/tmp")
        return {
            "excel_dir": str(temp_dir / "uploads"),
            "csv_dir": str(temp_dir / "converted"),
            "output_dir": str(temp_dir / "output"),
        }
    else:
        # 本地开发时的默认路径
        root = Path(__file__).resolve().parent.parent
        return {
            "excel_dir": str(root / "数据转换" / "数据源"),
            "csv_dir": str(root / "数据转换" / "转换后数据"),
            "output_dir": str(root / "数据转换" / "car-insurance-dashboard" / "data"),
        }


@app.route("/", methods=["GET"])
def index():
    paths = default_paths()
    return render_template("index.html", app_name=APP_NAME, paths=paths, result=None)


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
    start = time.time()
    paths = {
        "excel_dir": request.form.get("excel_dir", "").strip(),
        "csv_dir": request.form.get("csv_dir", "").strip(),
        "output_dir": request.form.get("output_dir", "").strip(),
    }

    result: Dict[str, Any] = {"ok": False, "summary": {}, "messages": []}

    try:
        module = load_preprocessor_module()

        excel_dir = Path(paths["excel_dir"]).expanduser()
        csv_dir = Path(paths["csv_dir"]).expanduser()
        output_dir = Path(paths["output_dir"]).expanduser()

        # 1) Excel → CSV
        converted = module.convert_excel_to_csv(excel_dir, csv_dir)
        result["messages"].append(f"Excel 转 CSV：{len(converted)} 个文件")

        # 2) 预处理（按年度输出 + 元数据）
        restructurer = module.CarInsuranceDataRestructurer()
        summary = restructurer.process_all_files(str(csv_dir), str(output_dir))

        # 3) 更新元数据
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
        flash("处理完成", "success")

    except Exception as exc:
        result["ok"] = False
        result["messages"].append(f"处理失败: {exc}")
        flash("处理失败", "error")

    return render_template("index.html", app_name=APP_NAME, paths=paths, result=result)


@app.route("/upload", methods=["GET", "POST"])
def upload_files():
    """文件上传功能，适配云端部署"""
    if request.method == "GET":
        return render_template("upload.html", app_name=APP_NAME)

    try:
        if 'files' not in request.files:
            return {"ok": False, "message": "未选择文件"}

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return {"ok": False, "message": "未选择文件"}

        # 创建临时上传目录
        upload_dir = Path("/tmp/claude/uploads") if os.environ.get("TMPDIR") else Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        uploaded_files = []
        for file in files:
            if file and file.filename and file.filename.endswith(('.xlsx', '.csv')):
                filename = file.filename
                file_path = upload_dir / filename
                file.save(str(file_path))
                uploaded_files.append(filename)

        return {
            "ok": True,
            "message": f"成功上传 {len(uploaded_files)} 个文件",
            "files": uploaded_files,
            "upload_dir": str(upload_dir)
        }

    except Exception as exc:
        return {"ok": False, "message": f"上传失败: {exc}"}, 500


@app.post("/download")
def download_zip():
    output_dir = request.form.get("output_dir", "").strip()
    out_path = Path(output_dir)
    if not out_path.exists() or not out_path.is_dir():
        flash("无效的输出目录，无法打包下载", "error")
        return redirect(url_for("index"))

    # 将目录打包为内存 zip 并返回
    memfile = io.BytesIO()
    with zipfile.ZipFile(memfile, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in out_path.rglob("*"):
            if p.is_file():
                arcname = p.relative_to(out_path)
                zf.write(p, arcname=str(arcname))
    memfile.seek(0)

    filename = f"data-preprocessed-{int(time.time())}.zip"
    return send_file(
        memfile,
        as_attachment=True,
        download_name=filename,
        mimetype="application/zip",
    )


# Vercel需要导出app对象
# 不需要if __name__ == "__main__"

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
    """动态加载 数据转换/数据预处理脚本.py 模块"""
    import importlib.util

    project_root = Path(__file__).resolve().parent.parent
    script_path = project_root / "数据转换" / "数据预处理脚本.py"
    if not script_path.exists():
        raise FileNotFoundError(f"未找到数据预处理脚本: {script_path}")

    spec = importlib.util.spec_from_file_location("data_preprocessor", str(script_path))
    module = importlib.util.module_from_spec(spec)  # type: ignore
    if spec and spec.loader:
        spec.loader.exec_module(module)  # type: ignore
    else:
        raise RuntimeError("无法加载数据预处理脚本模块")
    return module


def default_paths() -> Dict[str, str]:
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


@app.get("/pick")
def pick_directory():
    """在服务器端打开系统目录选择器并返回所选路径"""
    target = request.args.get("target", "")
    try:
        # 优先使用 tkinter 打开本机目录选择窗口
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.update()
            path = filedialog.askdirectory(title=f"选择{target or '数据'}目录")
            root.destroy()

            if path:
                return {"ok": True, "path": path}
        except Exception:
            pass

        # macOS 备用方案：AppleScript 选择目录
        import subprocess
        script = 'POSIX path of (choose folder with prompt "选择目录" default location (path to desktop))'
        out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
        if out:
            return {"ok": True, "path": out}

        return {"ok": False, "message": "已取消选择或无法获取目录"}

    except Exception as exc:
        # 返回错误信息
        return {"ok": False, "message": f"无法打开目录选择器: {exc}"}, 500


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


if __name__ == "__main__":
    # 生产环境配置
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug)

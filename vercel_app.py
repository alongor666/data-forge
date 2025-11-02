#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel Serverless适配文件
用于Vercel部署的WSGI应用入口
"""

import os
import sys

# 确保必要的目录存在
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = '处理后'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入主要的Flask应用
from app import app

# Vercel需要暴露的WSGI应用
application = app

# 确保生产环境配置
if os.environ.get('VERCEL_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
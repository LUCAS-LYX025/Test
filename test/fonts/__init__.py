# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: __init__.py
@time: 2025/9/28 13:00
"""
import os

import streamlit as st
script_dir = os.path.dirname(os.path.abspath(__file__))
st.success(f"📁 脚本所在目录123: `{script_dir}`")


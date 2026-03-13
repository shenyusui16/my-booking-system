import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="小幸孕預約管理", layout="wide")

# 2. 高級視覺美化 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 2em; }
    .noon-header { background-color: #7d7db3; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 18px; }
    .night-header { background-color: #6da37d; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 18px; }
    .table-container { border: 1px solid #ddd; border-radius: 0 0 8px 8px; background-color: white; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #333;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"

# 3. 定義你要的【完美排序】
# 右邊看板顯示順序
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務"]
all_cols = ["日期", "時段"] + display_cols

# 4. 讀取資料並自動校正欄位 (避免資料不見)
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    # 修正舊欄位名稱相容性
    if "醫院" in df.columns:
        df = df.rename(columns={"醫院": "產檢醫院"})
    # 確保所有要求的欄位都存在
    for col in all_cols:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單輸入 (順序已固定) ---
with st.sidebar:
    st.markdown("### 📝 預約表單")
    is_editing = 'edit_index' in st.session_state
    
    if is_editing:
        st.error(f"⚠️ 正在編輯：{st.session_state.edit_name}")
        if st.button("放棄修改"):
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

    with st.form("main_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        f_date = col_s1.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = col_s2.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""))
        
        st.markdown("---")
        # 左側欄位順序同步
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁寬度與標題
st.set_page_config(page_title="小幸孕預約管理", layout="wide")

# 自定義 CSS 讓表格和按鈕更好看
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 2em; }
    .noon-header { background-color: #7d7db3; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .night-header { background-color: #6da37d; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #333;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
# 看板要顯示的順序
display_cols = ["預約時間", "姓名", "電話", "醫院", "天數", "業務", "來源", "預產期", "住址", "禁忌"]
all_cols = ["日期", "時段"] + display_cols

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    for col in all_cols:
        if col not in df.columns: df[col] = ""
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：新增/修改 ---
with st.sidebar:
    st.markdown("### 📝 預約表單")
    is_editing = 'edit_index' in st.session_state
    
    if is_editing:
        st.error(f"⚠️ 正在修改：{st.session_state.edit_name}")
        if st.button("放棄修改"):
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

    with st.form("main_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        f_date = col_s1.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = col_s2.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間 (11:30-12:30)", value=st.session_state.get('edit_time', ""))
        
        st.markdown("---")
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due

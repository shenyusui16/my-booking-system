import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="小幸孕預約系統", layout="wide")

# 標題樣式
st.markdown("<h1 style='text-align: center; color: #5D5D5D;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
display_cols = ["預約時間", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務"]
all_cols = ["日期", "時段"] + display_cols

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    for col in all_cols:
        if col not in df.columns: df[col] = ""
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單輸入 ---
with st.sidebar:
    st.header("📝 登記/修改表單")
    # 如果 session 裡有資料，代表正在編輯模式
    is_editing = 'edit_index' in st.session_state
    
    if is_editing:
        st.warning(f"正在修改：{st.session_state.edit_name}")
        if st.button("取消修改"):
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

    with st.form("main_form", clear_on_submit=True):
        f_date = st.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = st.selectbox("預約時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""), placeholder="例如 11:30-12:30")
        
        st.divider()
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due', datetime.now()))
        f_hosp = st.text_input("醫院", value=st.session_state.get('edit_hosp', ""))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=1, value=int(st.session_state.get('edit_days', 1)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        
        submitted = st.form_submit_button("確認儲存" if is_editing else "確認提交登記")
        
        if submitted:
            new_data = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale
            }
            if is_editing:
                df = df.drop(st.session_state.edit_index)
            
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("成功！")
            st.rerun()

# --- 主畫面：美化看板 ---
col_date, col_empty = st.columns([3, 7])
with col_date:
    target_date = st.date_input("📅 選擇查看日期", datetime.now())

t_str = str(target_date)
view_df = df[df["日期"] == t_str].copy()

def render_styled_table(slot_name, color, bg_light):
    st.markdown(f"<div style='background-color:{color}; color:white; padding:8px 15px; border-radius:5px 5px 0 0; font-weight:bold;'>{slot_name}預約名單 ({t_str})</div>", unsafe_allow_html=True)
    
    slot_df = view_df[view_df["時段"] == slot_name].sort_values("預約時間")
    
    if not slot_df.empty:
        # 顯示專業表格
        st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
        
        # 表格下方的快速管理區
        with st.expander(f"⚙️ 管理{slot_name}

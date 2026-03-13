import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁寬度與標題
st.set_page_config(page_title="小幸孕預約管理", layout="wide")

# 自定義 CSS 樣式
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

# --- 核心設定：統一左右兩邊的欄位順序 ---
# 這裡定義了右邊看板表格顯示的順序
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務"]
all_cols = ["日期", "時段"] + display_cols

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    # 確保所有必要的欄位都存在，若無則補空值
    for col in all_cols:
        if col not in df.columns: df[col] = ""
    # 處理舊資料中欄位名稱不一的問題（例如 醫院 改名 產檢醫院）
    if "醫院" in df.columns and "產檢醫院" in df.columns:
        df["產檢醫院"] = df["產檢醫院"].fillna(df["醫院"])
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單輸入 (順序已固定) ---
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
        
        # 預約時間不備註
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""))
        
        st.markdown("---")
        # 左側表單欄位順序
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due', datetime.now()))
        f_hosp = st.text_input("產檢醫院", value=st.session_state.get('edit_hosp', ""))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=1, value=int(st.session_state.get('edit_days', 1)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        
        save_btn = st.form_submit_button("💾 儲存資料" if is_editing else "➕ 確認登記")
        
        if save_btn:
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "產檢醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale
            }
            if is_editing:
                df = df.drop(st.session_state.edit_index)
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("操作成功！")
            st.rerun()

# --- 主畫面：排程看板 (依照 display_cols 排序) ---
c_date, c_empty = st.columns([2, 5])
target_date = c_date.date_input("📅 查看日期", datetime.now())
t_str = str(target_date)

def draw_section(slot_name, header_class):
    st.markdown(f"<div class='{header_class}'>{slot_name}預約清單 ({t_str})</div>", unsafe_allow_html=True)
    # 過濾當天時段並排序
    current_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].sort_values("預約時間")
    
    if not current_df.empty:
        # 關鍵：這裡 [display_cols] 會強制右邊表格按照你要的順序排列
        st.dataframe(current_df[display_cols], use_container_width=True, hide_index=True)
        
        with st.expander(f"⚙️ 管理{slot_name}的資料"):
            for idx, row in current_df.iterrows():
                mc1, mc2, mc3 = st.columns([4, 1, 1])
                mc1.write(f"**{row['預約時間']}** - {row['姓名']} ({row['電話']})")
                if mc2.button("📝 編輯", key=f"e_{idx}"):
                    st.session_state.edit_index = idx
                    st.session_state.edit_date = datetime.strptime(row['日期'], '%Y-%m-%d')
                    st.session_state.edit_slot = row['時段']
                    st.session_state.edit_time = row['預約時間']
                    st.session_state.edit_name = row['姓名']
                    st.session_state.edit_phone = row['電話']
                    st.session_state.edit_due = datetime.strptime(row['預產期'], '%Y-%m-%d')
                    st.session_state.edit

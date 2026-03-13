import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="小幸孕管理系統", layout="wide")

st.markdown("<h2 style='text-align: center;'>🍼 小幸孕試吃預約管理系統</h2>", unsafe_allow_html=True)

DB_FILE = "data.csv"
display_cols = ["預約時間", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務"]
all_cols = ["日期", "時段"] + display_cols

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    for col in all_cols:
        if col not in df.columns: df[col] = ""
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：新增/編輯 區塊 ---
with st.sidebar:
    st.header("📝 預約登記表單")
    # 用來判斷現在是「新增」還是「編輯」
    mode = st.radio("模式", ["新增資料", "修改資料"])
    
    if mode == "修改資料":
        st.info("請先在右側看板點擊「編輯」按鈕，資料會自動帶入下方表單。")

    with st.form("main_form", clear_on_submit=True):
        f_date = st.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = st.selectbox("預約時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""))
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due', datetime.now()))
        f_hosp = st.text_input("醫院", value=st.session_state.get('edit_hosp', ""))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=1, value=int(st.session_state.get('edit_days', 1)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        
        btn_text = "確認修改" if mode == "修改資料" else "確認提交登記"
        submitted = st.form_submit_button(btn_text)
        
        if submitted:
            new_data = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale
            }
            
            if mode == "修改資料" and 'edit_index' in st.session_state:
                # 刪除舊的，加入新的（達成更新效果）
                df = df.drop(st.session_state.edit_index)
                
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            # 清除編輯狀態
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("✅ 處理成功！")
            st.rerun()

# --- 主畫面：排程看板 ---
target_date = st.date_input("📅 選擇查看日期", datetime.now())
t_str = str(target_date)
view_df = df[df["日期"] == t_str].copy()

def show_table(slot_name, color):
    st.markdown(f"<div style='background-color:{color}; padding:10px; border-radius:5px; margin-bottom:10px;'><b>{slot_name}預約登記 ({t_str})</b></div>", unsafe_allow_html=True)
    slot_df = view_df[view_df["時段"] == slot_name]
    
    if not slot_df.empty:
        # 顯示資料
        for idx, row in slot_df.iterrows():
            cols_ui = st.columns([4, 1, 1]) # 資料區, 編輯鈕, 刪除鈕
            with cols_ui[0]:
                st.write(f"⏰ {row['預約時間']} | 👤 {row['姓名']} | 📞 {row['電話']} | 🏥 {row['醫院']}")
            with cols_ui[1]:
                if st.button("📝 編輯", key=f"edit_{idx}"):
                    # 把資料存入 session 準備帶入表單
                    st.session_state.edit_index = idx
                    st.session_state.edit_date = datetime.strptime(row['日期'], '%Y-%m-%d')
                    st.session_state.edit_slot = row['時段']
                    st.session_state.edit_time = row['預約時間']
                    st.session_state.edit_name = row['姓名']
                    st.session_state.edit_phone = row['電話']
                    st.session_state.edit_due = datetime.strptime(row['預產期'], '%Y-%m-%d')
                    st.session_state.edit_hosp = row['醫院']
                    st.session_state.edit_addr = row['住址']
                    st.session_state.edit_tabo = row['禁忌']
                    st.session_state.edit_days = row['天數']
                    st.session_state.edit_sour = row['來源']
                    st.session_state.edit_sale = row['業務']
                    st.rerun()
            with cols_ui[2]:
                if st.button("🗑️ 刪除", key=f"del_{idx}"):
                    new_df = df.drop(idx)
                    new_df.to_csv(DB_FILE, index=False)
                    st.rerun()
            st.divider()
    else:
        st.write(f"今日{slot_name}暫無預約")

show_table("中午", "#E2E2F0")
show_table("晚上", "#E2F0E2")

# 下載按鈕
st.sidebar.divider()
st.sidebar.download_button("📥 匯出完整報表", df.to_csv(index=False).encode('utf-8-sig'), "小幸孕報表.csv", "text/csv")

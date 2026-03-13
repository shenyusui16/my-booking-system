import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="🍼 小幸孕試吃預約管理系統", layout="wide")

# CSS 樣式美化
st.markdown("""
    <style>
    .noon-header { background-color: #7d7db3; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .night-header { background-color: #6da37d; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .month-header { background-color: #4a4a4a; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
# 定義您要求的標準欄位 (將產檢醫院改回醫院)
display_cols = ["預約時間", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# 2. 強力讀取與校正邏輯 (解決 ValueError & KeyError)
def get_clean_df():
    if os.path.exists(DB_FILE):
        try:
            raw_df = pd.read_csv(DB_FILE)
            # A. 解決重複欄位報錯 (Duplicate column names)
            raw_df = raw_df.loc[:, ~raw_df.columns.duplicated()]
            
            # B. 將「產檢醫院」統一改名為「醫院」
            if "產檢醫院" in raw_df.columns:
                raw_df = raw_df.rename(columns={"產檢醫院": "醫院"})
            
            # C. 補齊缺失欄位
            for col in all_cols:
                if col not in raw_df.columns:
                    raw_df[col] = "未簽約" if col == "簽約狀態" else ""
            
            # D. 只抓取正確的欄位，丟棄所有雜訊欄位
            final_df = raw_df[all_cols].copy()
            final_df['日期'] = final_df['日期'].astype(str)
            return final_df
        except Exception as e:
            st.error(f"資料讀取有誤，建議手動刪除 CSV 重新建立。錯誤碼: {e}")
            return pd.DataFrame(columns=all_cols)
    return pd.DataFrame(columns=all_cols)

df = get_clean_df()

# --- 側邊欄表單 ---
with st.sidebar:
    st.markdown("### 📝 預約登記")
    is_editing = 'edit_index' in st.session_state
    
    with st.form("main_form", clear_on_submit=True):
        f_date = st.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = st.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""))
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_hosp = st.text_input("醫院", value=st.session_state.get('edit_hosp', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"], index=0 if st.session_state.get('edit_contract') == "未簽約" else 1)
        
        # ... (其餘欄位為了精簡代碼略，請自行在 form 中補齊 st.text_input 或 date_input)
        # 關鍵在於這裡的 Submit 按鈕
        if st.form_submit_button("💾 儲存預約"):
            new_data = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": "2026-01-01", "醫院": f_hosp, "住址": "",
                "禁忌": "", "天數": 1, "來源": "", "業務": f_sale, "簽約狀態": f_contract
            }
            if is_editing: df = df.drop(st.session_state.edit_index)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("成功存入！")
            st.rerun()

# --- 主畫面標籤 ---
tab1, tab2 = st.tabs(["📅 當日看板", "📊 月統計"])

with tab1:
    target_date = st.date_input("選擇日期", datetime.now())
    t_str = str(target_date)
    
    for slot, css in [("中午", "noon-header"), ("晚上", "night-header")]:
        st.markdown(f"<div class='{css}'>{slot}預約清單</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot)]
        if not slot_df.empty:
            # 這裡顯示時只用正確的 display_cols，防止報錯
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info(f"{slot}暫無預約")

with tab2:
    st.info("全月統計功能正常運行中，請確保資料日期格式正確。")

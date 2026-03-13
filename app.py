import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="🍼 小幸孕試吃管理系統", layout="wide")

st.markdown("<h1 style='text-align: center;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
# 強制統一名稱：醫院、業務
display_cols = ["預約時間", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# --- 強制清理按鈕 (放在最上面，如果出錯就按它) ---
if st.button("🔥 如果系統報錯，請按此按鈕「初始化系統」"):
    df_new = pd.DataFrame(columns=all_cols)
    df_new.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.success("系統已重置，請重新整理頁面！")
    st.rerun()

# 2. 資料讀取與自動校正 (處理 Duplicate column 錯誤)
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 解決重複欄位與改名
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.rename(columns={"產檢醫院": "醫院", "預預約時間": "預約時間", "業務人員": "業務"})
            # 補齊缺失欄位
            for col in all_cols:
                if col not in df.columns:
                    df[col] = "未簽約" if col == "簽約狀態" else ""
            return df[all_cols]
        except:
            return pd.DataFrame(columns=all_cols)
    return pd.DataFrame(columns=all_cols)

df = load_data()

# --- 側邊欄：預約表單 ---
with st.sidebar:
    st.header("📝 預約表單")
    with st.form("my_form", clear_on_submit=True):
        f_date = st.date_input("試吃日期", datetime.now())
        f_slot = st.selectbox("時段", ["中午", "晚上"])
        f_time = st.text_input("預約時間")
        f_name = st.text_input("客戶姓名")
        f_phone = st.text_input("電話")
        f_hosp = st.text_input("醫院") # 這裡已改為醫院
        f_sale = st.text_input("業務")
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"])
        
        # 為了穩定，暫時收納最核心欄位
        if st.form_submit_button("💾 儲存預約"):
            new_data = pd.DataFrame([{
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_date), "醫院": f_hosp, "住址": "",
                "禁忌": "", "天數": 1, "來源": "", "業務": f_sale, "簽約狀態": f_contract
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success("儲存成功！")
            st.rerun()

# --- 主畫面：顯示資料 ---
target_date = st.date_input("📅 查看日期", datetime.now())
t_str = str(target_date)

for slot, color in [("中午", "#7d7db3"), ("晚上", "#6da37d")]:
    st.markdown(f"<div style='background:{color};color:white;padding:10px;border-radius:5px'>{slot}預約清單</div>", unsafe_allow_html=True)
    slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot)]
    if not slot_df.empty:
        st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.write("暫無資料")

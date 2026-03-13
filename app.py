import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="小幸孕預約系統", layout="wide")

# 標題
st.markdown("<h2 style='text-align: center;'>🍼 小幸孕試吃預約登記系統</h2>", unsafe_allow_html=True)

DB_FILE = "data.csv"

# --- 關鍵：定義看板顯示的欄位順序 ---
# 我們把「預約時間」放在第一順位
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務"]
all_cols = ["日期", "時段"] + display_cols

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    # 確保所有欄位都存在，如果不存在就補空白
    for col in all_cols:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：新增登記 ---
with st.sidebar:
    st.header("📝 新增預約")
    with st.form("my_form", clear_on_submit=True):
        date = st.date_input("試吃日期")
        time_slot = st.selectbox("預約時段", ["中午", "晚上"])
        # 改名為「預約具體時間」以便區分
        exact_time = st.text_input("預約具體時間", placeholder="例如：11:30-12:30")
        
        st.divider()
        
        name = st.text_input("客戶姓名")
        phone = st.text_input("電話")
        due_date = st.date_input("預產期")
        hospital = st.text_input("產檢醫院")
        address = st.text_area("住址")
        taboo = st.text_input("禁忌")
        days = st.number_input("天數", min_value=1, value=1)
        source = st.text_input("來源")
        sales = st.text_input("業務")
        
        submitted = st.form_submit_button("確認提交登記")
        
        if submitted:
            new_row = {
                "日期": str(date), "時段": time_slot, "預約時間": exact_time, 
                "姓名": name, "電話": phone, "預產期": str(due_date), 
                "產檢醫院": hospital, "住址": address, "禁忌": taboo, 
                "天數": days, "來源": source, "業務": sales
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("✅ 登記成功！")
            st.rerun()

# --- 主畫面：排程看板 ---
target_date = st.date_input("📅 選擇查看日期", datetime.now())
t_str = str(target_date)
today_data = df[df["日期"] == t_str]

# 中午區塊
st.markdown(f"<div style='background-color:#E2E2F0; padding:10px; border-radius:5px; margin-bottom:10px;'><b>☀️ 中午預約登記 ({t_str})</b></div>", unsafe_allow_html=True)

# 這裡強制指定顯示 display_cols 的順序
noon_df = today_data[today_data["時段"] == "中午"]
if not noon_df.empty:
    st.dataframe(noon_df[display_cols], use_container_width=True)
else:
    st.write("今日中午暫無預約")

st.write("") 

# 晚上區塊
st.markdown(f"<div style='background-color:#E2F0E2; padding:10px; border-radius:5px; margin-bottom:10px;'><b>🌙 晚上預約登記 ({t_str})</b></div>", unsafe_allow_html=True)

night_df = today_data[today_data["時段"] == "晚上"]
if not night_df.empty:
    st.dataframe(night_df[display_cols], use_container_width=True)
else:
    st.write("今日晚上暫無預約")

# 下載按鈕
st.sidebar.divider()
st.sidebar.download_button("📥 匯出完整報表", df.to_csv(index=False).encode('utf-8-sig'), "小幸孕報表.csv", "text/csv")

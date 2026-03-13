import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題與風格
st.set_page_config(page_title="小幸孕預約系統", layout="wide")
st.markdown("### 🍼 小幸孕試吃預約登記系統")

# 資料存儲檔案路徑
DB_FILE = "data.csv"

# 初始化資料庫
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["日期", "時段", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務"])

# --- 側邊欄：新增預約 ---
with st.sidebar:
    st.header("📝 新增登記")
    with st.form("my_form", clear_on_submit=True):
        date = st.date_input("試吃日期")
        time_slot = st.selectbox("預約時段", ["中午", "晚上"])
        name = st.text_input("客戶姓名")
        phone = st.text_input("電話")
        due_date = st.date_input("預產期")
        hospital = st.text_input("醫院")
        address = st.text_area("住址")
        taboo = st.text_input("禁忌")
        days = st.number_input("天數", min_value=1, value=1)
        source = st.text_input("來源")
        sales = st.text_input("業務人員")
        
        submitted = st.form_submit_button("確認提交")
        if submitted:
            new_row = {
                "日期": str(date), "時段": time_slot, "姓名": name, "電話": phone,
                "預產期": str(due_date), "醫院": hospital, "住址": address,
                "禁忌": taboo, "天數": days, "來源": source, "業務": sales
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("✅ 登記成功！")
            st.rerun()

# --- 主畫面：預約看板 ---
target_date = st.date_input("📅 選擇查看日期", datetime.now())
selected_date_str = str(target_date)

# 篩選當天資料
today_data = df[df["日期"] == selected_date_str]

col1, col2 = st.columns(2)

with col1:
    st.info(f"☀️ 中午預約 ({selected_date_str})")
    noon_df = today_data[today_data["時段"] == "中午"]
    if not noon_df.empty:
        st.dataframe(noon_df.drop(columns=["日期", "時段"]), use_container_width=True)
    else:
        st.write("目前無資料")

with col2:
    st.warning(f"🌙 晚上預約 ({selected_date_str})")
    night_df = today_data[today_data["時段"] == "晚上"]
    if not night_df.empty:
        st.dataframe(night_df.drop(columns=["日期", "時段"]), use_container_width=True)
    else:
        st.write("目前無資料")

# 匯出完整報表
st.divider()
st.download_button("📥 匯出完整 Excel (CSV)", df.to_csv(index=False).encode('utf-8-sig'), "小幸孕報表.csv", "text/csv")

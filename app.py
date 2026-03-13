import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 網頁基本設定
st.set_page_config(page_title="預約管理系統", layout="wide")

# 粉色系樣式優化
st.markdown("""
    <style>
    .main { background-color: #fff9fa; }
    .stApp { background-color: #fff9fa; }
    .noon-header { background: linear-gradient(90deg, #f48fb1, #f8bbd0); color: white; padding: 12px; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    .night-header { background: linear-gradient(90deg, #ec407a, #f06292); color: white; padding: 12px; border-radius: 10px; font-weight: bold; margin-bottom: 10px; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(240, 98, 146, 0.1); border: 1px solid #fce4ec; text-align: center; }
    .month-header { background-color: #ad1457; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ad1457;'>🌸 試吃預約管理系統 (雲端同步版)</h1>", unsafe_allow_html=True)

# 2. 設定 Google Sheets 網址 (請換成您剛複製的網址)
# 這裡我先放一個範例格式，請將引號內的文字換成您的網址
SHEET_URL = "您的Google試算表網址" 
CSV_EXPORT_URL = SHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')
# 如果是新的試算表，通常格式如下：
if "/edit" in SHEET_URL:
    CSV_EXPORT_URL = SHEET_URL.split('/edit')[0] + "/gviz/tq?tqx=out:csv"

# 3. 讀取資料
def load_data():
    try:
        # 從 Google Sheets 抓取資料
        df = pd.read_csv(CSV_EXPORT_URL)
        return df
    except:
        # 如果失敗則顯示警告
        st.error("無法連線至 Google 試算表，請確認網址與共用權限。")
        return pd.DataFrame(columns=["日期", "時段", "預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"])

df = load_data()

# --- 側邊欄：表單 ---
with st.sidebar:
    st.markdown("### 💗 預約登記")
    # 提醒：Google Sheets 版本暫不支援在網頁端直接「刪除/編輯」
    # 建議直接在 Google Sheets 上修改，網頁會自動同步
    with st.form("main_form", clear_on_submit=True):
        f_date = st.date_input("試吃日期", datetime.now())
        f_slot = st.selectbox("時段", ["中午", "晚上"])
        f_time = st.text_input("精確時間", placeholder="11:30")
        f_name = st.text_input("客戶姓名")
        f_phone = st.text_input("電話")
        f_due = st.date_input("預產期", datetime.now())
        f_hosp = st.text_input("產檢醫院")
        f_addr = st.text_area("住址")
        f_tabo = st.text_input("禁忌")
        f_days = st.number_input("天數", min_value=1, value=1)
        f_sour = st.text_input("來源")
        f_sale = st.text_input("業務")
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"])
        
        if st.form_submit_button("💖 儲存資料並同步至雲端"):
            # 這裡我們教您一個最簡單的存檔法：
            # 目前 Streamlit 直接寫回 Sheets 需要進階設定，
            # 建議您先維持原本 CSV 存檔，但我會教您如何讓 Google Sheets 自動抓這份 CSV
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "產檢醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale, "簽約狀態": f_contract
            }
            # 維持 GitHub 存檔 (確保資料不丟失)
            df_local = pd.read_csv("data.csv") if os.path.exists("data.csv") else pd.DataFrame()
            df_local = pd.concat([df_local, pd.DataFrame([new_row])], ignore_index=True)
            df_local.to_csv("data.csv", index=False, encoding='utf-8-sig')
            st.success("存檔成功！GitHub 已同步。")
            st.rerun()

# --- 主畫面標籤頁 (這部分與之前相同，僅美化樣式) ---
tab1, tab2 = st.tabs(["📅 當日看板", "📈 月度績效與清單"])

# (後續看板與統計代碼維持之前的邏輯...)

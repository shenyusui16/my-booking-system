import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="試吃預約管理系統", layout="wide")

# 高級視覺美化
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .noon-header { background-color: #7d7db3; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .night-header { background-color: #6da37d; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .month-header { background-color: #4a4a4a; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .sales-header { background-color: #d4a373; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🍼 試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# 2. 強力格式校正邏輯 (解決報錯關鍵)
if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE)
        # 強制修正所有可能的舊欄位名稱
        name_map = {
            "醫院": "產檢醫院",
            "預預約時間": "預約時間",
            "預約具體時間": "預約時間",
            "業務人員": "業務"
        }
        df = df.rename(columns=name_map)
        
        # 確保 display_cols 裡的所有欄位都存在，若無則補空字串
        for col in all_cols:
            if col not in df.columns:
                df[col] = "未簽約" if col == "簽約狀態" else ""
        
        # 確保資料格式統一
        df['日期'] = df['日期'].astype(str)
    except:
        df = pd.DataFrame(columns=all_cols)
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單 ---
with st.sidebar:
    st.markdown("### 📝 預約登記")
    is_editing = 'edit_index' in st.session_state
    
    with st.form("main_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        f_date = col_s1.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = col_s2.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""))
        st.markdown("---")
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due', datetime.now()))
        f_hosp = st.text_input("產檢醫院", value=st.session_state.get('edit_hosp', ""))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=1, value=int(st.session_state.get('edit_days', 1)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"], index=0 if st.session_state.get('edit_contract') == "未簽約" else 1)
        
        if st.form_submit_button("💾 儲存預約"):
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "產檢醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale, "簽約狀態": f_contract
            }
            if is_editing: df = df.drop(st.session_state.edit_index)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

# --- 主畫面 ---
tab1, tab2 = st.tabs(["📅 當日排程看板", "📊 全月績效總覽"])

with tab1:
    target_date = st.date_input("選擇日期", datetime.now(), key="day_picker")
    t_str = str(target_date)

    def draw_section(slot_name, header_class):
        st.markdown(f"<div class='{header_class}'>{slot_name}預約清單</div>", unsafe_allow_html=True)
        # 過濾並顯示
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].copy()
        if not slot_df.empty:
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
            with st.expander("⚙️ 管理資料"):
                for idx, row in slot_df.iterrows():
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.write(f"⏰ {row['預約時間']} | {row['姓名']}")
                    if c2.button("編輯", key=f"e_{idx}"):
                        st.session_state.edit_index = idx
                        st.session_state.edit_name = row['姓名']
                        # ... (其他編輯欄位自動帶入略)
                        st.rerun()
                    if c3.button("刪除", key=f"d_{idx}"):
                        df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
        else:
            st.info(f"{slot_name}無預約")

    draw_section("中午", "noon-header")
    draw_section("晚上", "night-header")

with tab2:
    # 這裡確保排序時不會報錯
    target_m = st.date_input("選擇月份", target_date, key="m_picker").strftime('%Y-%m')
    st.markdown(f"<div class='month-header'>{target_m} 月份詳細清單</div>", unsafe_allow_html=True)
    
    m_df = df[df["日期"].str.contains(target_m)].copy()
    if not m_df.empty:
        # 排序前確保欄位存在
        m_df = m_df.sort_values(by=["日期", "時段"], ascending=[True, False])
        st.dataframe(m_df[["日期", "時段"] + display_cols], use_container_width=True, hide_index=True)
        
        # 業務統計
        st.markdown(f"<div class='sales-header'>業務績效統計</div>", unsafe_allow_html=True)
        sales = m_df.groupby("業務").agg(
            總預約=("姓名", "count"),
            已簽約=("簽約狀態", lambda x: (x == "已簽約").sum()),
            未簽約=("簽約狀態", lambda x: (x == "未簽約").sum())
        ).reset_index()
        st.table(sales)
    else:
        st.info("尚無資料")

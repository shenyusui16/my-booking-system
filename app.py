import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="預約管理系統", layout="wide")

# 自定義視覺樣式 (保留粉色調，但移除複雜字體)
st.markdown("""
    <style>
    .main { background-color: #fff9fa; }
    .stApp { background-color: #fff9fa; }
    
    /* 標題與標籤 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] {
        background-color: #f06292 !important;
        color: white !important;
    }

    /* 漸層標題列 */
    .section-header { 
        background-color: #f06292; 
        color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; margin: 20px 0 10px 0;
    }

    /* 數據卡片 */
    .metric-card {
        background-color: white; padding: 15px; border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
        border: 1px solid #fce4ec; text-align: center;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #ad1457; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ad1457;'>🌸 試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
# 標準欄位定義 (醫院已回歸電話後方)
all_cols = ["日期", "時段", "預約時間", "姓名", "電話", "醫院", "預產期", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 欄位補全
            for col in all_cols:
                if col not in df.columns: df[col] = ""
            return df[all_cols]
        except:
            return pd.DataFrame(columns=all_cols)
    return pd.DataFrame(columns=all_cols)

df = load_data()

# --- 側邊欄：表單 ---
with st.sidebar:
    st.markdown("### 💗 預約登記")
    is_editing = 'edit_index' in st.session_state
    with st.form("main_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        f_date = col_s1.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = col_s2.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') != "晚上" else 1)
        f_time = st.text_input("精確時間", value=st.session_state.get('edit_time', ""), placeholder="例如 11:30")
        st.markdown("---")
        f_name = st.text_input("客戶姓名", value=st.session_state.get('edit_name', ""))
        f_phone = st.text_input("電話", value=st.session_state.get('edit_phone', ""))
        f_hosp = st.text_input("醫院", value=st.session_state.get('edit_hosp', ""))
        f_due = st.date_input("預產期", value=st.session_state.get('edit_due', datetime.now()))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=0, value=int(st.session_state.get('edit_days', 0)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"], index=0 if st.session_state.get('edit_contract') != "已簽約" else 1)
        
        if st.form_submit_button("💖 儲存資料"):
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "醫院": f_hosp, "預產期": str(f_due), "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale, "簽約狀態": f_contract
            }
            if is_editing:
                df = df.drop(st.session_state.edit_index)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("存檔成功！")
            st.rerun()

# --- 主畫面標籤頁 ---
tab1, tab2 = st.tabs(["📅 當日看板", "📈 月度數據總覽"])

with tab1:
    target_date = st.date_input("選擇日期", datetime.now())
    t_str = str(target_date)
    for slot in ["中午", "晚上"]:
        st.markdown(f"<div class='section-header'>{slot}預約清單</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"].astype(str) == t_str) & (df["時段"] == slot)]
        if not slot_df.empty:
            st.dataframe(slot_df[["預約時間", "姓名", "電話", "醫院", "業務", "簽約狀態"]], use_container_width=True, hide_index=True)
        else:
            st.info(f"目前無{slot}預約")

with tab2:
    st.markdown("<div class='section-header'>📊 本月數據統計</div>", unsafe_allow_html=True)
    col_y, col_m = st.columns(2)
    sel_year = col_y.selectbox("年份", range(2025, 2030), index=1)
    sel_month = col_m.selectbox("月份", range(1, 13), index=datetime.now().month-1)
    month_prefix = f"{sel_year}-{sel_month:02d}"
    
    month_df = df[df["日期"].astype(str).str.startswith(month_prefix)].copy()
    
    if not month_df.empty:
        # 數據卡片
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'>總預約人數<div class='metric-value'>{len(month_df)}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'>已簽約件數<div class='metric-value' style='color:#2e7d32;'>{len(month_df[month_df['簽約狀態']=='已簽約'])}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'>未簽約件數<div class='metric-value' style='color:#c62828;'>{len(month_df[month_df['簽約狀態']!='已簽約'])}</div></div>", unsafe_allow_html=True)
        
        # 業務統計表 (核心修改)
        st.markdown("<div class='section-header'>🏆 各業務績效統計</div>", unsafe_allow_html=True)
        month_df['業務'] = month_df['業務'].replace('', '未填寫').fillna('未填寫')
        
        sales_summary = month_df.groupby('業務').agg(
            預約人數=('姓名', 'count'),
            已簽約件數=('簽約狀態', lambda x: (x == '已簽約').sum()),
            未簽約件數=('簽約狀態', lambda x: (x != '已簽約').sum())
        ).reset_index()
        
        st.dataframe(sales_summary, use_container_width=True, hide_index=True)
        
        # 月度所有原始名單
        st.markdown("<div class='section-header'>📋 本月完整名單清單</div>", unsafe_allow_html=True)
        st.dataframe(month_df.sort_values(["日期", "時段"]), use_container_width=True, hide_index=True)
    else:
        st.warning(f"目前無 {month_prefix} 的資料")

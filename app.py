import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="月子餐預約系統", layout="wide")

# 2. 自定義視覺樣式 (加入可愛質感字體與漸層)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&family=Noto+Sans+TC:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    h1, h2, h3, .month-header {
        font-family: 'ZCOOL XiaoWei', serif;
    }

    .main { background-color: #fff9fa; }
    .stApp { background-color: #fff9fa; }

    /* 頂部標題 */
    .main-title {
        text-align: center;
        color: #d81b60;
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* 漸層標題列 */
    .month-header { 
        background: linear-gradient(135deg, #ff80ab, #f06292); 
        color: white; 
        padding: 12px 20px; 
        border-radius: 15px; 
        font-weight: bold; 
        margin-top: 25px;
        box-shadow: 0 4px 15px rgba(240, 98, 146, 0.2);
    }

    /* 數據卡片升級 */
    .metric-card {
        background: white; 
        padding: 25px; 
        border-radius: 20px; 
        box-shadow: 0 10px 20px rgba(240, 98, 146, 0.1); 
        border: 1px solid #fce4ec; 
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }

    /* 側邊欄按鈕 */
    .stButton>button {
        border-radius: 25px;
        border: 2px solid #f06292;
        background-color: white;
        color: #f06292;
        font-weight: bold;
        padding: 10px 25px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #f06292, #ff80ab);
        color: white;
        border: 2px solid transparent;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌸 專屬預約管理看板</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
all_cols = ["日期", "時段", "預約時間", "姓名", "電話", "醫院", "預產期", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in all_cols:
                if col not in df.columns: df[col] = ""
            return df[all_cols]
        except:
            return pd.DataFrame(columns=all_cols)
    return pd.DataFrame(columns=all_cols)

df = load_data()

# --- 側邊欄：表單 ---
with st.sidebar:
    st.markdown("### 💗 填寫預約紀錄")
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
        f_sale = st.text_input("業務人員", value=st.session_state.get('edit_sale', ""))
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"], index=0 if st.session_state.get('edit_contract') != "已簽約" else 1)
        
        if st.form_submit_button("💖 確認送出"):
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
            st.success("紀錄已存檔！")
            st.rerun()

# --- 主畫面標籤頁 ---
tab1, tab2 = st.tabs(["📅 當日看板", "📈 業務戰績月報表"])

with tab1:
    target_date = st.date_input("選擇日期查詢", datetime.now())
    t_str = str(target_date)
    for slot, color in [("中午", "linear-gradient(90deg, #f48fb1, #f8bbd0)"), ("晚上", "linear-gradient(90deg, #ec407a, #f06292)")]:
        st.markdown(f"<div style='background:{color}; color:white; padding:10px; border-radius:10px; margin-top:15px; font-weight:bold;'>{slot} 預約</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"].astype(str) == t_str) & (df["時段"] == slot)]
        if not slot_df.empty:
            st.dataframe(slot_df[["預約時間", "姓名", "電話", "醫院", "業務", "簽約狀態"]], use_container_width=True, hide_index=True)
        else:
            st.caption(f"目前無{slot}預約")

with tab2:
    st.markdown("<div class='month-header'>📊 本月業績表現概覽</div>", unsafe_allow_html=True)
    col_y, col_m = st.columns(2)
    sel_year = col_y.selectbox("年份", range(2025, 2030), index=1)
    sel_month = col_m.selectbox("月份", range(1, 13), index=datetime.now().month-1)
    month_prefix = f"{sel_year}-{sel_month:02d}"
    
    month_df = df[df["日期"].astype(str).str.startswith(month_prefix)].copy()
    
    if not month_df.empty:
        # 數據卡片區
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'>總預約人數<div class='metric-value' style='color:#ad1457;'>{len(month_df)}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'>已簽約件數<div class='metric-value' style='color:#2e7d32;'>{len(month_df[month_df['簽約狀態']=='已簽約'])}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'>待追蹤件數<div class='metric-value' style='color:#f57c00;'>{len(month_df[month_df['簽約狀態']!='已簽約'])}</div></div>", unsafe_allow_html=True)
        
        # 各業務績效統計 (核心需求)
        st.markdown("<div class='month-header'>🏆 各業務戰績排行榜</div>", unsafe_allow_html=True)
        month_df['業務'] = month_df['業務'].replace('', '未填寫').fillna('未填寫')
        
        # 建立統計表格
        sales_summary = month_df.groupby('業務').agg(
            預約人數=('姓名', 'count'),
            已簽約件數=('簽約狀態', lambda x: (x == '已簽約').sum()),
            未簽約件數=('簽約狀態', lambda x: (x == '未簽約').sum())
        ).reset_index()
        
        # 計算轉換率並美化顯示
        sales_summary['轉換率'] = (sales_summary['已簽約件數'] / sales_summary['預約人數'] * 100).round(1).astype(str) + '%'
        
        # 顯示美化過的表格
        st.dataframe(
            sales_summary.sort_values("已簽約件數", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # 月度所有原始資料
        st.markdown("<div class='month-header'>📋 本月所有試吃名單</div>", unsafe_allow_html=True)
        st.dataframe(month_df.sort_values(["日期", "時段"]), use_container_width=True, hide_index=True)
    else:
        st.warning(f"目前還沒有 {month_prefix} 的預約資料喔！")

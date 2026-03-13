import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="小幸孕預約管理", layout="wide")

# 自定義視覺樣式
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .noon-header { background-color: #7d7db3; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .night-header { background-color: #6da37d; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .month-header { background-color: #4a4a4a; color: white; padding: 10px; border-radius: 8px 8px 0 0; font-weight: bold; margin-top: 20px; }
    .stats-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #7d7db3; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🍼 小幸孕試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"

# 2. 定義欄位 (增加「簽約狀態」)
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# 3. 讀取並自動修復資料結構
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 確保所有欄位都存在
            for col in all_cols:
                if col not in df.columns:
                    df[col] = "未簽約" if col == "簽約狀態" else ""
            return df
        except:
            return pd.DataFrame(columns=all_cols)
    return pd.DataFrame(columns=all_cols)

df = load_data()

# --- 側邊欄：表單 ---
with st.sidebar:
    st.markdown("### 📝 預約表單")
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
        
        save_btn = st.form_submit_button("💾 儲存資料")
        if save_btn:
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "產檢醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale, "簽約狀態": f_contract
            }
            if is_editing:
                df = df.drop(st.session_state.edit_index)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            # 清除編輯狀態
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

# --- 主畫面標籤頁 ---
tab1, tab2 = st.tabs(["📅 當日排程看板", "📊 全月預約與統計"])

with tab1:
    target_date = st.date_input("📅 選擇查看日期", datetime.now())
    t_str = str(target_date)

    def draw_section(slot_name, header_class):
        st.markdown(f"<div class='{header_class}'>{slot_name}預約清單 ({t_str})</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].copy()
        
        if not slot_df.empty:
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
            with st.expander(f"⚙️ 管理{slot_name}資料"):
                for idx, row in slot_df.iterrows():
                    mc1, mc2, mc3 = st.columns([4, 1, 1])
                    mc1.write(f"⏰ **{row['預約時間']}** | 👤 {row['姓名']} ({row['業務']} - {row['簽約狀態']})")
                    if mc2.button("編輯", key=f"e_{idx}"):
                        st.session_state.edit_index = idx
                        st.session_state.edit_date = datetime.strptime(str(row['日期']), '%Y-%m-%d')
                        st.session_state.edit_slot = row['時段']
                        st.session_state.edit_time = row['預約時間']
                        st.session_state.edit_name = row['姓名']
                        st.session_state.edit_phone = row['電話']
                        st.session_state.edit_due = datetime.strptime(str(row['預產期']), '%Y-%m-%d')
                        st.session_state.edit_hosp = row['產檢醫院']
                        st.session_state.edit_addr = row['住址']
                        st.session_state.edit_tabo = row['禁忌']
                        st.session_state.edit_days = row['天數']
                        st.session_state.edit_sour = row['來源']
                        st.session_state.edit_sale = row['業務']
                        st.session_state.edit_contract = row['簽約狀態']
                        st.rerun()
                    if mc3.button("刪除", key=f"d_{idx}"):
                        df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
        else:
            st.info(f"{slot_name}暫無預約資料")

    draw_section("中午", "noon-header")
    draw_section("晚上", "night-header")

with tab2:
    st.markdown("### 📊 全月數據分析")
    # 月份選擇器
    month_to_show = st.date_input("選擇統計月份", datetime.now()).strftime('%Y-%m')
    
    # 篩選該月資料
    month_df = df[df["日期"].str.startswith(month_to_show)].copy()
    
    if not month_df.empty:
        # 1. 頂部總結數字
        c1, c2, c3 = st.columns(3)
        total_p = len(month_df)
        signed_p = len(month_df[month_df["簽約狀態"] == "已簽約"])
        unsigned_p = len(month_df[month_df["簽約狀態"] == "未簽約"])
        
        c1.metric("本月總預約人數", f"{total_p} 人")
        c2.metric("已簽約人數", f"{signed_p} 人")
        c3.metric("未簽約人數", f"{unsigned_p} 人")
        
        # 2. 業務績效表
        st.markdown("<div class='month-header'>🏆 業務簽約績效統計</div>", unsafe_allow_html=True)
        # 處理業務名稱為空值的情況
        month_df['業務'] = month_df['業務'].fillna('未填寫').replace('', '未填寫')
        
        sales_stats = month_df.groupby('業務').agg(
            總預約數=('姓名', 'count'),
            已簽約件數=('簽約狀態', lambda x: (x == '已簽約').sum()),
            未簽約件數=('簽約狀態', lambda x: (x == '未簽約').sum())
        ).reset_index()
        
        # 計算轉化率
        sales_stats['轉化率'] = (sales_stats['已簽約件數'] / sales_stats['總預約數'] * 100).round(1).astype(str) + '%'
        st.table(sales_stats)
        
        # 3. 全月預約詳細清單
        st.markdown(f"<div class='month-header'>📅 {month_to_show} 全月預約詳細清單</div>", unsafe_allow_html=True)
        # 依照日期排序顯示
        st.dataframe(month_df.sort_values("日期"), use_container_width=True, hide_index=True)
    else:
        st.warning(f"目前尚無 {month_to_show} 的預約資料")

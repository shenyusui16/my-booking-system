import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="試吃預約管理系統", layout="wide")

# 自定義視覺樣式 (粉色溫馨風格)
st.markdown("""
    <style>
    .main { background-color: #fff9fa; }
    .stApp { background-color: #fff9fa; }
    
    /* 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #fce4ec;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #880e4f;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f06292 !important;
        color: white !important;
        font-weight: bold;
    }

    /* 中午與晚上標題 */
    .noon-header { 
        background: linear-gradient(90deg, #f48fb1, #f8bbd0); 
        color: white; padding: 12px; border-radius: 10px; font-weight: bold; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .night-header { 
        background: linear-gradient(90deg, #ec407a, #f06292); 
        color: white; padding: 12px; border-radius: 10px; font-weight: bold; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* 月度統計標題 */
    .month-header { 
        background-color: #ad1457; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; 
    }

    /* 數據卡片 */
    .metric-card {
        background-color: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(240, 98, 146, 0.1); 
        border: 1px solid #fce4ec;
        text-align: center;
    }
    
    /* 側邊欄按鈕 */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #f06292;
        color: #f06292;
    }
    .stButton>button:hover {
        background-color: #f06292;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ad1457;'>🌸 試吃預約管理系統</h1>", unsafe_allow_html=True)

DB_FILE = "data.csv"
# 標準欄位定義
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 欄位補全與修復
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
    st.markdown("### 💗 預約登記")
    is_editing = 'edit_index' in st.session_state
    
    with st.form("main_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        f_date = col_s1.date_input("試吃日期", value=st.session_state.get('edit_date', datetime.now()))
        f_slot = col_s2.selectbox("時段", ["中午", "晚上"], index=0 if st.session_state.get('edit_slot') == "中午" else 1)
        f_time = st.text_input("預約時間", value=st.session_state.get('edit_time', ""), placeholder="例如 11:30")
        
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
        
        if st.form_submit_button("💖 儲存資料"):
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "產檢醫院": f_hosp, "住址": f_addr,
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
tab1, tab2 = st.tabs(["📅 當日看板", "📈 月度績效與清單"])

with tab1:
    target_date = st.date_input("請選擇查看日期", datetime.now())
    t_str = str(target_date)

    def draw_section(slot_name, header_class):
        st.markdown(f"<div class='{header_class}'>{slot_name}預約清單</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].copy()
        
        if not slot_df.empty:
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
            with st.expander(f"⚙️ 修改/刪除 {slot_name} 資料"):
                for idx, row in slot_df.iterrows():
                    mc1, mc2, mc3 = st.columns([4, 1, 1])
                    mc1.write(f"⏰ **{row['預約時間']}** | 👤 {row['姓名']} ({row['業務']})")
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
            st.info(f"{slot_name}目前沒有預約資料")

    draw_section("中午", "noon-header")
    draw_section("晚上", "night-header")

with tab2:
    st.markdown("### 📊 月度數據總覽")
    
    # 月份選擇
    col_y, col_m = st.columns(2)
    current_year = datetime.now().year
    sel_year = col_y.selectbox("選擇年份", range(current_year-1, current_year+2), index=1)
    sel_month = col_m.selectbox("選擇月份", range(1, 13), index=datetime.now().month-1)
    month_to_show = f"{sel_year}-{sel_month:02d}"
    
    month_df = df[df["日期"].str.startswith(month_to_show)].copy()
    
    if not month_df.empty:
        # 1. 數據卡片
        total_p = len(month_df)
        signed_p = len(month_df[month_df["簽約狀態"] == "已簽約"])
        unsigned_p = len(month_df[month_df["簽約狀態"] == "未簽約"])
        
        st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div class="metric-card" style="flex: 1; border-top: 5px solid #f06292;">
                <p style="color: #888; margin: 0;">本月總預約</p>
                <h2 style="margin: 0; color: #ad1457;">{total_p} <span style="font-size: 16px;">人</span></h2>
            </div>
            <div class="metric-card" style="flex: 1; border-top: 5px solid #6da37d;">
                <p style="color: #888; margin: 0;">已簽約</p>
                <h2 style="margin: 0; color: #2e7d32;">{signed_p} <span style="font-size: 16px;">件</span></h2>
            </div>
            <div class="metric-card" style="flex: 1; border-top: 5px solid #e57373;">
                <p style="color: #888; margin: 0;">未簽約</p>
                <h2 style="margin: 0; color: #c62828;">{unsigned_p} <span style="font-size: 16px;">件</span></h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. 業務統計
        st.markdown("<div class='month-header'>🏆 各業務績效統計</div>", unsafe_allow_html=True)
        month_df['業務'] = month_df['業務'].fillna('未填寫').replace('', '未填寫')
        sales_stats = month_df.groupby('業務').agg(
            總預約數=('姓名', 'count'),
            已簽約件數=('簽約狀態', lambda x: (x == '已簽約').sum()),
            未簽約件數=('簽約狀態', lambda x: (x == '未簽約').sum())
        ).reset_index()
        sales_stats['轉化達成率'] = (sales_stats['已簽約件數'] / sales_stats['總預約數'] * 100).round(1).astype(str) + '%'
        st.table(sales_stats)
        
        # 3. 月份詳細清單
        st.markdown(f"<div class='month-header'>📅 {sel_month} 月份完整預約清單</div>", unsafe_allow_html=True)
        st.dataframe(month_df.sort_values(["日期", "時段"]), use_container_width=True, hide_index=True)
    else:
        st.warning(f"目前尚無 {month_to_show} 的預約資料")

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="試吃預約管理系統", layout="wide")

# 高級視覺美化 CSS
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

# 2. 定義欄位排序 (與您的要求完全一致)
display_cols = ["預約時間", "姓名", "電話", "預產期", "產檢醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# 3. 讀取並自動校正資料結構 (防錯機制)
if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE)
        # 自動修復舊欄位名稱或缺失欄位
        if "預預約時間" in df.columns: df = df.rename(columns={"預預約時間": "預約時間"})
        if "醫院" in df.columns: df = df.rename(columns={"醫院": "產檢醫院"})
        for col in all_cols:
            if col not in df.columns:
                df[col] = "未簽約" if col == "簽約狀態" else ""
    except:
        df = pd.DataFrame(columns=all_cols)
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單輸入 ---
with st.sidebar:
    st.markdown("### 📝 預約登記")
    is_editing = 'edit_index' in st.session_state
    
    if is_editing:
        st.warning(f"正在編輯: {st.session_state.get('edit_name')}")
        if st.button("取消編輯"):
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.rerun()

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
            st.success("存檔成功！")
            st.rerun()

# --- 主畫面：標籤頁分流 ---
tab1, tab2 = st.tabs(["📅 當日排程看板", "📊 全月績效總覽"])

with tab1:
    target_date = st.date_input("選擇日期", datetime.now(), key="day_picker")
    t_str = str(target_date)

    def draw_day_section(slot_name, header_class):
        st.markdown(f"<div class='{header_class}'>{slot_name}預約清單</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].copy()
        if not slot_df.empty:
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
            with st.expander(f"⚙️ 管理資料"):
                for idx, row in slot_df.iterrows():
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.write(f"⏰ **{row['預約時間']}** | 👤 {row['姓名']} ({row['業務']})")
                    if c2.button("編輯", key=f"e_{idx}"):
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
                    if c3.button("刪除", key=f"d_{idx}"):
                        df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
        else:
            st.info(f"{slot_name}暫無預約")

    draw_day_section("中午", "noon-header")
    draw_day_section("晚上", "night-header")

with tab2:
    target_month_date = st.date_input("選擇月份 (點選任一天即可)", datetime.now(), key="month_picker")
    current_month = target_month_date.strftime('%Y-%m')
    st.markdown(f"<div class='month-header'>{current_month} 月份清單</div>", unsafe_allow_html=True)
    
    month_df = df[df["日期"].str.startswith(current_month)].copy()
    if not month_df.empty:
        # 正確排序，解決 KeyError
        month_df = month_df.sort_values(by=["日期", "時段", "預約時間"], ascending=[True, False, True])
        st.dataframe(month_df[["日期", "時段"] + display_cols], use_container_width=True, hide_index=True)
        
        # --- 業務績效報表 ---
        st.markdown(f"<div class='sales-header'>{current_month} 業務績效統計</div>", unsafe_allow_html=True)
        
        sales_stats = []
        unique_sales = [s for s in month_df["業務"].unique() if str(s) != "nan" and str(s) != ""]
        
        for sale in unique_sales:
            sale_data = month_df[month_df["業務"] == sale]
            total = len(sale_data)
            signed = len(sale_data[sale_data["簽約狀態"] == "已簽約"])
            unsigned = len(sale_data[sale_data["簽約狀態"] == "未簽約"])
            rate = f"{(signed/total)*100:.1f}%" if total > 0 else "0%"
            sales_stats.append({
                "業務姓名": sale,
                "總預約": total,
                "已簽約": signed,
                "未簽約": unsigned,
                "簽約率": rate
            })
        
        if sales_stats:
            st.table(pd.DataFrame(sales_stats))
        else:
            st.write("本月尚未登記業務姓名")
            
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("全月預約總計", len(month_df))
        m2.metric("全月已簽約", len(month_df[month_df["簽約狀態"] == "已簽約"]))
        m3.metric("全月未簽約", len(month_df[month_df["簽約狀態"] == "未簽約"]))
    else:
        st.info(f"{current_month} 尚無資料")

# 匯出按鈕
st.sidebar.divider()
st.sidebar.download_button("📥 下載完整 CSV 備份", df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), f"預約備份_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

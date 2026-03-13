import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 網頁基本設定
st.set_page_config(page_title="試吃預約管理系統", layout="wide")

# CSS 樣式美化
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
# 定義標準欄位 (已將「產檢醫院」改回「醫院」)
display_cols = ["預約時間", "姓名", "電話", "預產期", "醫院", "住址", "禁忌", "天數", "來源", "業務", "簽約狀態"]
all_cols = ["日期", "時段"] + display_cols

# 2. 資料讀取與「強力自動校正」邏輯
if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE)
        
        # A. 強制修正所有可能的舊欄位名稱或錯誤名稱
        name_map = {
            "產檢醫院": "醫院",
            "預預約時間": "預約時間",
            "預約具體時間": "預約時間",
            "業務人員": "業務"
        }
        df = df.rename(columns=name_map)
        
        # B. 徹底移除重複的欄位 (解決 Duplicate column names 錯誤)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # C. 補齊缺失欄位，並確保顯示順序正確
        for col in all_cols:
            if col not in df.columns:
                df[col] = "未簽約" if col == "簽約狀態" else ""
        
        # D. 只保留我們定義的欄位，丟棄多餘的亂碼欄位
        df = df[all_cols]
        
        # E. 確保日期格式正確
        df['日期'] = df['日期'].astype(str)
        
    except Exception as e:
        st.error(f"系統自動修復中，請稍候... (錯誤訊息: {e})")
        df = pd.DataFrame(columns=all_cols)
else:
    df = pd.DataFrame(columns=all_cols)

# --- 側邊欄：表單輸入 ---
with st.sidebar:
    st.markdown("### 📝 預約登記")
    # 編輯模式檢查
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
        f_hosp = st.text_input("醫院", value=st.session_state.get('edit_hosp', ""))
        f_addr = st.text_area("住址", value=st.session_state.get('edit_addr', ""))
        f_tabo = st.text_input("禁忌", value=st.session_state.get('edit_tabo', ""))
        f_days = st.number_input("天數", min_value=1, value=int(st.session_state.get('edit_days', 1)))
        f_sour = st.text_input("來源", value=st.session_state.get('edit_sour', ""))
        f_sale = st.text_input("業務", value=st.session_state.get('edit_sale', ""))
        f_contract = st.selectbox("簽約狀態", ["未簽約", "已簽約"], index=0 if st.session_state.get('edit_contract') == "未簽約" else 1)
        
        submit_label = "💾 更新預約" if is_editing else "💾 儲存預約"
        if st.form_submit_button(submit_label):
            new_row = {
                "日期": str(f_date), "時段": f_slot, "預約時間": f_time, "姓名": f_name,
                "電話": f_phone, "預產期": str(f_due), "醫院": f_hosp, "住址": f_addr,
                "禁忌": f_tabo, "天數": f_days, "來源": f_sour, "業務": f_sale, "簽約狀態": f_contract
            }
            if is_editing:
                df = df.drop(st.session_state.edit_index)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            
            # 清除編輯狀態
            for key in list(st.session_state.keys()):
                if key.startswith('edit_'): del st.session_state[key]
            st.success("存檔成功！")
            st.rerun()

# --- 主畫面：標籤頁 ---
tab1, tab2 = st.tabs(["📅 當日排程看板", "📊 全月績效總覽"])

with tab1:
    target_date = st.date_input("選擇日期", datetime.now(), key="day_picker")
    t_str = str(target_date)

    def draw_day_section(slot_name, header_class):
        st.markdown(f"<div class='{header_class}'>{slot_name}預約清單</div>", unsafe_allow_html=True)
        slot_df = df[(df["日期"] == t_str) & (df["時段"] == slot_name)].copy()
        
        if not slot_df.empty:
            st.dataframe(slot_df[display_cols], use_container_width=True, hide_index=True)
            with st.expander(f"⚙️ 修改/刪除 {slot_name} 資料"):
                for idx, row in slot_df.iterrows():
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.write(f"⏰ {row['預約時間']} | {row['姓名']} ({row['業務']})")
                    if c2.button("編輯", key=f"edit_btn_{idx}"):
                        st.session_state.edit_index = idx
                        st.session_state.edit_date = datetime.strptime(str(row['日期']), '%Y-%m-%d')
                        st.session_state.edit_slot = row['時段']
                        st.session_state.edit_time = row['預約時間']
                        st.session_state.edit_name = row['姓名']
                        st.session_state.edit_phone = row['電話']
                        st.session_state.edit_due = datetime.strptime(str(row['預產期']), '%Y-%m-%d')
                        st.session_state.edit_hosp = row['醫院']
                        st.session_state.edit_addr = row['住址']
                        st.session_state.edit_tabo = row['禁忌']
                        st.session_state.edit_days = row['天數']
                        st.session_state.edit_sour = row['來源']
                        st.session_state.edit_sale = row['業務']
                        st.session_state.edit_contract = row['簽約狀態']
                        st.rerun()
                    if c3.button("刪除", key=f"del_btn_{idx}"):
                        df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
        else:
            st.info(f"{slot_name}暫無預約")

    draw_day_section("中午", "noon-header")
    draw_day_section("晚上", "night-header")

with tab2:
    target_m = st.date_input("選擇查看月份", target_date, key="month_picker").strftime('%Y-%m')
    st.markdown(f"<div class='month-header'>{target_m} 月份詳細清單</div>", unsafe_allow_html=True)
    
    m_df = df[df["日期"].str.contains(target_m)].copy()
    
    if not m_df.empty:
        # 排序：日期、時段
        m_df = m_df.sort_values(by=["日期", "時段"], ascending=[True, False])
        st.dataframe(m_df[["日期", "時段"] + display_cols], use_container_width=True, hide_index=True)
        
        # 業務績效報表
        st.markdown("<div class='sales-header'>業務績效統計</div>", unsafe_allow_html=True)
        # 確保業務欄位沒有空值
        m_df['業務'] = m_df['業務'].replace('', '未標記')
        
        stats = m_df.groupby("業務").agg(
            總預約=("姓名", "count"),
            已簽約=("簽約狀態", lambda x: (x == "已簽約").sum()),
            未簽約=("簽約狀態", lambda x: (x == "未簽約").sum())
        ).reset_index()
        
        # 計算達成率
        stats['簽約率'] = (stats['已簽約'] / stats['總預約'] * 100).map('{:.1f}%'.format)
        st.table(stats)
    else:
        st.info(f"{target_m} 尚無任何紀錄")

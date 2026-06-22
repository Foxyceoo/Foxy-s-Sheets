import streamlit as st
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

# URL Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsybhqY890uEGLVqXyvC9Ovlfi-eXjjiIQ0jLMVDGc1TIaimWkLmT6F7RlI5DsWg/pub?gid=1844334473&single=true&output=csv"

# 2. Hàm load dữ liệu
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        if 'Loại' not in df.columns:
            for i in range(min(5, len(df))):
                if 'Loại' in df.iloc[i].values:
                    df = df[i+1:].reset_index(drop=True)
                    df.columns = df.iloc[0]
                    break
        df = df.dropna(subset=['Loại', 'Tên nhạc'])
        df['Loại'] = df['Loại'].astype(str).str.strip().str.lower()
        return df
    except Exception:
        return pd.DataFrame()

# 3. Main Logic
try:
    with st.spinner("Đang tải dữ liệu..."):
        df = load_data()
        
    if df.empty:
        st.error("Không thể tải được dữ liệu từ Google Sheet.")
    else:
        st.title("🎵 Kho Sheet Nhạc")
        
        tab_filter = st.radio("Chọn xem:", ["all","event","free","txt","nber"], horizontal=True)
        filtered_df = df.copy()
        
        if tab_filter != "all":
            filtered_df = filtered_df[filtered_df['Loại'] == tab_filter]

        search = st.text_input("🔍 Tìm tên bài hát...")
        if search:
            filtered_df = filtered_df[filtered_df['Tên nhạc'].astype(str).str.contains(search, case=False, na=False)]

        # --- ĐƯỜNG KẺ PHÍA TRÊN NẰM TRONG ELSE ĐỂ KHÔNG BỊ LỖI ---
        st.markdown("---")

        # --- ĐƯỜNG KẺ PHÍA TRÊN NẰM TRONG ELSE ĐỂ KHÔNG BỊ LỖI ---
        st.markdown("---")

        for index, row in filtered_df.iterrows():
            ten_nhac = str(row.get('Tên nhạc', 'Không tên')).replace('*', '')
            loai = str(row.get('Loại', '')).strip()
            casi = row.get('Ca sĩ / nhạc sĩ', 'N/A')
            trans = row.get('Transcripted', 'N/A')
            gia = str(row.get('VND', '0')).strip()
            download_url = str(row.get('Download', '')).strip()
            test_url = str(row.get('Test', '')).strip()
            
            is_dl = download_url.lower().startswith('http')
            is_test = test_url.lower().startswith('http')

            # TẤT CẢ CÁC DÒNG NÀY PHẢI THỤT VÀO TRONG VÒNG LẶP FOR
            st.markdown(f'<h3 style="font-size: 25px; margin-top: 0px; margin-bottom: 0px;">{ten_nhac}</h3>', unsafe_allow_html=True)
            
            st.markdown(f'<div style="font-size: 18px; font-weight: bold; color: #555; margin-top: 0px; margin-bottom: 10px;">🎤 {casi} | ✍️ Trans: {trans}</div>', unsafe_allow_html=True)
                
            st.markdown(f'''
                <div style="display: flex; gap: 5px; margin: 0px;">
                    <a href="{test_url if is_test else '#'}" target="_blank" style="flex: 1; text-decoration:none;">
                        <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#ff7400' if is_test else '#ffcab2'}; color:white; cursor:{'pointer' if is_test else 'not-allowed'};">▶</button>
                    </a>            
                    <a href="{download_url if is_dl else '#'}" target="_blank" style="flex: 3; text-decoration:none;">
                        <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#b2d600' if is_dl else '#cbd695'}; color:white; cursor:{'pointer' if is_dl else 'not-allowed'};">
                            {'Tải về' if is_dl and (loai in ['free', 'event']) else (f'Mua: {gia}' if is_dl else 'Đang cập nhật')}
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
                
            st.markdown('<hr style="margin: 5px 0px; border: 0; border-top: 1px solid #ccc;">', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Đã có lỗi xảy ra: {e}")

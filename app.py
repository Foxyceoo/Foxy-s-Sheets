import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

# URL Sheet của cậu
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsybhqY890uEGLVqXyvC9Ovlfi-eXjjiIQ0jLMVDGc1TIaimWkLmT6F7RlI5DsWg/pub?gid=1844334473&single=true&output=csv"

@st.cache_data(ttl=30) # Để TTL 30s giúp ổn định hơn
def load_data():
    df_raw = pd.read_csv(SHEET_URL)
    # Tìm dòng chứa Header
    for i in range(len(df_raw)):
        if 'Loại' in df_raw.iloc[i].values:
            df = df_raw[i+1:].copy()
            df.columns = df_raw.iloc[i]
            break
    else:
        df = df_raw
    df.columns = [str(c).strip() for c in df.columns]
    if 'Loại' in df.columns:
        df['Loại'] = df['Loại'].astype(str).str.strip().str.lower()
    return df.dropna(subset=['Loại', 'Tên nhạc'])

try:
    df = load_data()
    st.title("🎵 Kho Sheet Nhạc")
    
    tab_filter = st.radio("Chọn xem:", ["all","event","free","txt","nber"], horizontal=True)
    filtered_df = df.copy()
    if tab_filter != "all":
        filtered_df = filtered_df[filtered_df['Loại'] == tab_filter.lower()]

    search = st.text_input("🔍 Tìm tên bài hát...")
    if search:
        filtered_df = filtered_df[filtered_df['Tên nhạc'].astype(str).str.contains(search, case=False, na=False)]

    st.markdown("---")

    for index, row in filtered_df.iterrows():
        ten_nhac = str(row.get('Tên nhạc', 'Không tên')).replace('*', '')
        loai = str(row.get('Loại', '')).strip()
        casi = row.get('Ca sĩ / nhạc sĩ', 'N/A')
        download_url = str(row.get('Download', '')).strip()
        test_url = str(row.get('Test', '')).strip()
        is_dl = download_url.lower().startswith('http')
        is_test = test_url.lower().startswith('http')

        # Chia cột: Cột trái (Tên nhạc + Ca sĩ) 70%, Cột phải (2 Nút) 30%
        col_main, col_btn = st.columns([0.7, 0.3])
        
        with col_main:
            tag = {"event": "🎊", "nber": "🌟", "txt": "✨", "free": "✅"}.get(loai, "🎵")
            st.markdown(f"**{tag} {ten_nhac}**")
            st.caption(f"🎤 {casi}")
            
        with col_btn:
            # Dùng CSS Flexbox để ép 2 nút nằm sát nhau trên 1 hàng
            st.markdown(f'''
                <div style="display: flex; gap: 5px; margin-top: 10px;">
                    <a href="{test_url if is_test else '#'}" target="_blank" style="flex: 1; text-decoration:none;">
                        <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#ff4b4b' if is_test else '#d3d3d3'}; color:white; cursor:{'pointer' if is_test else 'not-allowed'};">▶</button>
                    </a>
                    <a href="{download_url if is_dl else '#'}" target="_blank" style="flex: 2; text-decoration:none;">
                        <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#ff4b4b' if is_dl else '#d3d3d3'}; color:white; cursor:{'pointer' if is_dl else 'not-allowed'};">
                            {'Tải' if is_dl else '...'}
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")

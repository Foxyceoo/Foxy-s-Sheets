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
        trans = row.get('Transcripted', 'N/A')
        gia = str(row.get('VND', '0')).strip()
        
        # Lấy link sạch
        download_url = str(row.get('Download', '')).strip()
        test_url = str(row.get('Test', '')).strip()
        
        # Kiểm tra tính hợp lệ của link (phải bắt đầu bằng http)
        is_dl = download_url.lower().startswith('http')
        is_test = test_url.lower().startswith('http')

        col1, col2 = st.columns([3, 1])
        with col1:
            tag = {"event": "🎊", "nber": "🌟", "txt": "✨", "free": "✅"}.get(loai, "🎵")
            st.markdown(f"**{tag} {ten_nhac}**")
            st.caption(f"🎤 {casi} | ✍️ Trans: {trans}")
            
        with col2:
            # Tạo khối div chứa 2 nút
            st.markdown(f'''
                <div style="display: flex; gap: 5px;">
                    <a href="{test_url}" target="_blank" style="flex: 1; text-decoration:none;">
                        <button style="width:100%; height:38px; border-radius:5px; border:none; background-color:{'#ff4b4b' if is_test else '#d3d3d3'}; color:white;">▶</button>
                    </a>
                    <a href="{download_url}" target="_blank" style="flex: 3; text-decoration:none;">
                        <button style="width:100%; height:38px; border-radius:5px; border:none; background-color:{'#ff4b4b' if is_dl else '#d3d3d3'}; color:white;">
                            {'Tải' if is_dl else '...'}
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown("---")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")

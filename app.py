import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

# Link Google Sheet của cậu
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsybhqY890uEGLVqXyvC9Ovlfi-eXjjiIQ0jLMVDGc1TIaimWkLmT6F7RlI5DsWg/pub?gid=1844334473&single=true&output=csv"

@st.cache_data(ttl=60) # Tăng ttl lên 60 giây để ổn định hơn
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
    
    # Làm sạch tên cột và dữ liệu
    df.columns = [str(c).strip() for c in df.columns]
    if 'Loại' in df.columns:
        df['Loại'] = df['Loại'].astype(str).str.strip().str.lower()
    
    return df.dropna(subset=['Loại', 'Tên nhạc'])

try:
    df = load_data()
    st.title("🎵 Kho Sheet Nhạc")
    
    tab_filter = st.radio("Chọn xem:", ["all", "event", "free", "txt", "nber"], horizontal=True)
    
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
        
        # Lấy link và dọn dẹp ký tự trắng
        download_url = str(row.get('Download', '')).strip()
        test_url = str(row.get('Test', '')).strip()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tag = {"event": "🎊", "nber": "🌟", "txt": "✨", "free": "✅"}.get(loai, "🎵")
            st.markdown(f"**{tag} {ten_nhac}**")
            st.caption(f"🎤 {casi} | ✍️ Trans: {trans}")
            
        with col2:
            sub1, sub2 = st.columns([1, 4]) 
            
            with sub1:
                # Nút Play
                is_test = (test_url.startswith('http') and len(test_url) > 5)
                color = "#ff4b4b" if is_test else "#d3d3d3"
                st.markdown(f'''
                    <a href="{test_url if is_test else '#'}" target="_blank" style="text-decoration:none;">
                        <button style="width: 35px; height: 35px; border-radius: 50%; border: none; background-color: {color}; color: white; cursor: {'pointer' if is_test else 'not-allowed'}; display: flex; align-items: center; justify-content: center; margin-top: 18px;">▶</button>
                    </a>
                ''', unsafe_allow_html=True)

            with sub2:
                st.markdown('<div style="margin-top: 11px;">', unsafe_allow_html=True)
                is_dl = (download_url.startswith('http') and len(download_url) > 5)
                btn_txt = "Tải về" if (loai in ['free', 'event']) else f"Mua: {gia}"
                color = "#ff4b4b" if is_dl else "#d3d3d3"
                
                st.markdown(f'''
                    <a href="{download_url if is_dl else '#'}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; border-radius:5px; border:none; padding:6px; background-color:{color}; color:white; cursor:{'pointer' if is_dl else 'not-allowed'};">{btn_txt if is_dl else 'Đang cập nhật'}</button>
                    </a>
                ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)            
        st.markdown("---")

except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")

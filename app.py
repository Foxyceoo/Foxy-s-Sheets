import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsybhqY890uEGLVqXyvC9Ovlfi-eXjjiIQ0jLMVDGc1TIaimWkLmT6F7RlI5DsWg/pub?gid=1844334473&single=true&output=csv"

@st.cache_data(ttl=5)
def load_data():
    df_raw = pd.read_csv(SHEET_URL)
    # Tìm dòng chứa Header
    for i in range(len(df_raw)):
        if 'Loại' in df_raw.iloc[i].values:
            new_header = df_raw.iloc[i]
            df = df_raw[i+1:].copy()
            df.columns = new_header
            break
    else:
        df = df_raw
    
    df.columns = [str(c).strip() for c in df.columns]
    if 'Loại' in df.columns:
        df['Loại'] = df['Loại'].astype(str).str.strip().str.lower()
    
    df = df.dropna(subset=['Loại', 'Tên nhạc'])
    return df

try:
    df = load_data()
    st.title("🎵 Kho Sheet Nhạc")
    
    options = ["all","event","free","txt","nber"]
    tab_filter = st.radio("Chọn xem:", options, horizontal=True)
    
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
        download_url = str(row.get('Download', '')).strip()
        test_url = str(row.get('Test', '')).strip()
        
        unique_key = f"btn_{index}"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if loai == 'event': tag = "🎊"
            elif loai == 'nber': tag = "🌟"
            elif loai == 'txt': tag = "✨"
            elif loai == 'free': tag = "✅"
            else: tag = "🎵"
            
            st.markdown(f"**{tag} {ten_nhac}**")
            st.caption(f"🎤 {casi} | ✍️ Trans: {trans}")
            
        with col2:
            subcol1, subcol2 = st.columns([1, 4]) 
            
            with subcol1:
                # Kiểm tra link Test
                is_test_valid = (test_url and test_url != '#' and test_url.lower() != 'nan' and len(test_url) > 5)
                if is_test_valid:
                    st.markdown(f'''
                        <a href="{test_url}" target="_blank" style="text-decoration:none;">
                            <button style="width: 35px; height: 35px; border-radius: 50%; border: none; background-color: #ff4b4b; color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; margin-top: 18px;">▶</button>
                        </a>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown('''
                        <button style="width: 35px; height: 35px; border-radius: 50%; border: none; background-color: #d3d3d3; color: white; cursor: not-allowed; display: flex; align-items: center; justify-content: center; margin-top: 18px;">▶</button>
                    ''', unsafe_allow_html=True)

            with subcol2:
                st.markdown('<div style="margin-top: 11px;">', unsafe_allow_html=True)
                
                # Kiểm tra link Download
                is_valid_download = (download_url and download_url != '#' and download_url.lower() != 'nan' and len(download_url) > 5)
                
                if is_valid_download:
                    btn_text = "Tải về" if (loai == 'free' or loai == 'event') else f"Mua: {gia}"
                    st.markdown(f'''
                        <a href="{download_url}" target="_blank" style="text-decoration:none;">
                            <button style="width:100%; border-radius:5px; border:none; padding:6px; background-color:#ff4b4b; color:white; cursor:pointer;">{btn_text}</button>
                        </a>
                    ''', unsafe_allow_html=True)
                else:
                    # Nút xám không nhấn được
                    st.markdown('''
                        <button style="width:100%; border-radius:5px; border:none; padding:6px; background-color:#d3d3d3; color:white; cursor:not-allowed;">Đang cập nhật</button>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)            
        st.markdown("---")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")

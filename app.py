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
            # Dùng st.columns để chia nút, không dùng HTML phức tạp để tránh lỗi render
            s1, s2 = st.columns([1, 2])
            with s1:
                if is_test:
                    st.link_button("▶", url=test_url, key=f"test_{index}")
                else:
                    st.button("▶", disabled=True, key=f"no_test_{index}")
            with s2:
                if is_dl:
                    label = "Tải về" if loai in ['free', 'event'] else f"Mua: {gia}"
                    st.link_button(label, url=download_url, key=f"dl_{index}")
                else:
                    st.button("Cập nhật", disabled=True, key=f"no_dl_{index}")
        st.markdown("---")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")

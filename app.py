import streamlit as st
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="Foxy.HQ", layout="centered")

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
        # Đặt Neo ở đầu trang
        st.markdown('<div id="top"></div>', unsafe_allow_html=True)
        st.title("--- Foxy.HQ ---")

        # --- ĐOẠN GIỚI THIỆU ---
        st.markdown("""
        Welcome to **Foxy.HQ** – The Official Foxy's Home!!!  
        Dedicated to creating and sharing the most chill Sky music sheets.  
           **Team:** Foxy, Harinezumi, Yexer  
           **Focus:** Music optimization and relaxing melodies for the Sky community.  
        Don't forget to Subscribe and join our chill journey!  
        """)

        # --- NÚT MẠNG XÃ HỘI CÓ LOGO (FONT AWESOME) ---
        st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)
        st.markdown("""
            <style>
            .social-btn { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; height: 38px; border-radius: 8px; text-decoration: none !important; color: white !important; font-weight: bold; }
            .social-btn:hover { filter: brightness(1.1); }
            </style>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<a href="https://www.facebook.com/foxy.ceo.o" target="_blank" class="social-btn" style="background-color: #1877F2;"><i class="fab fa-facebook"></i> Facebook</a>', unsafe_allow_html=True)
        with c2:
            st.markdown('<a href="https://www.youtube.com/@foxy.ceo.o" target="_blank" class="social-btn" style="background-color: #FF0000;"><i class="fab fa-youtube"></i> YouTube</a>', unsafe_allow_html=True)
        with c3:
            st.markdown('<a href="https://www.tiktok.com/@foxy.ceo.o" target="_blank" class="social-btn" style="background-color: #000000;"><i class="fab fa-tiktok"></i> TikTok</a>', unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- BỘ LỌC DẠNG TAB ---
        categories = ["all", "event", "free", "txt", "nber"]
        tabs = st.tabs([cat.upper() for cat in categories])
        
        # Tạo dict để lưu data cho từng tab
        tab_data = {cat: df.copy() for cat in categories}
        for cat in categories:
            if cat != "all":
                tab_data[cat] = df[df['Loại'] == cat]

        # Hiển thị nội dung trong từng Tab
        for i, tab in enumerate(tabs):
            cat = categories[i]
            with tab:
                # Lọc theo tìm kiếm trong từng tab
                search = st.text_input(f"Tìm tên bài hát trong mục {cat.upper()}... (viết không dấu)", key=f"search_{cat}")
                current_df = tab_data[cat]
                if search:
                    current_df = current_df[current_df['Tên nhạc'].astype(str).str.contains(search, case=False, na=False)]
                
                # --- VÒNG LẶP HIỂN THỊ BÀI HÁT TRONG TAB NÀY ---
                for index, row in current_df.iterrows():
                    ten_nhac = str(row.get('Tên nhạc', 'Không tên')).replace('*', '')
                    loai = str(row.get('Loại', '')).strip()
                    casi = row.get('Ca sĩ / nhạc sĩ', 'N/A')
                    trans = row.get('Transcripted', 'N/A')
                    gia = str(row.get('VND', '0')).strip()
                    download_url = str(row.get('Download', '')).strip()
                    test_url = str(row.get('Test', '')).strip()
                    
                    is_dl = download_url.lower().startswith('http')
                    is_test = test_url.lower().startswith('http')
                    is_anchor = download_url.strip() == "#top"

                    # Logic nút
                    if is_dl and (loai in ['free', 'event']):
                        btn_label, btn_link = 'Tải về', download_url
                    elif is_anchor:
                        btn_label, btn_link = f'Liên hệ mua: {gia}', "#top"
                    elif is_dl:
                        btn_label, btn_link = f'Liên hệ mua: {gia}', download_url
                    else:
                        btn_label, btn_link = 'Đang cập nhật', "#"

                    st.markdown(f'<h3 style="font-size: 24px; margin-top: 10px; margin-bottom: 0px;">{ten_nhac}</h3>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 15px; font-weight: bold; color: #555; margin-top: 0px; margin-bottom: 5px;">{casi} | Trans: {trans}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'''
                        <div style="display: flex; gap: 5px; margin-top: 0px; margin-bottom: 5px;">
                            <a href="{test_url if is_test else '#'}" target="_blank" style="flex: 1; text-decoration:none;">
                                <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#FF0000' if is_test else '#FFB2B2'}; color:white; cursor:{'pointer' if is_test else 'not-allowed'};">▶</button>
                            </a>
                            <a href="{btn_link}" target="{"_blank" if not is_anchor else "_self"}" style="flex: 3; text-decoration:none;">
                                <button style="width:100%; height:35px; border-radius:5px; border:none; background-color:{'#00008C' if is_dl or is_anchor else '#62628C'}; color:white; cursor:pointer;">
                                    {btn_label}
                                </button>
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.markdown('<hr style="margin: 0px 0px 10px 0px; border: 0; border-top: 1px solid #ddd;">', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Đã có lỗi xảy ra: {e}")

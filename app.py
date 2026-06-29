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
        st.markdown('<div id="top"></div>', unsafe_allow_html=True)
        st.title("--- Foxy.HQ ---")

        st.markdown("""
        Chào mừng đến với Foxy.HQ – Ngôi nhà chính thức của Foxy!!!  
        Chuyên sáng tạo và chia sẻ những sheet nhạc Sky "chill" nhất  
        Team: Foxy, Harinezumi, Yexer  
        Focus: Tối ưu hóa âm nhạc và mang đến những giai điệu thư giãn cho cộng đồng Sky  
        """)

        # --- NÚT BẢNG GIÁ (Đã sửa lại thụt lề) ---
        # --- NÚT BẢNG GIÁ (Có khung viền) ---
        with st.expander("💰 BẢNG GIÁ DỊCH VỤ"):
            st.markdown("""
                <style>
                .custom-box {
                    border: 2px solid #00008C; /* Viền màu xanh đậm */
                    border-radius: 10px;
                    padding: 15px;
                    background-color: #fcfcfc;
                }
                .price-table { width: 100%; border-collapse: collapse; color: #333; }
                .price-table th:nth-child(1) { background-color: #00008C; color: white; padding: 10px; }
                .price-table th:nth-child(2) { background-color: #FF0000; color: white; padding: 10px; }
                .price-table th:nth-child(3) { background-color: #00008C; color: white; padding: 10px; }
                .price-table td { padding: 10px; border: 1px solid #ddd; text-align: left; }
                </style>
                
                <div class="custom-box">
                    <table class="price-table">
                        <tr><th>Loại hình</th><th>Đơn giá</th><th>Ghi chú</th></tr>
                        <tr><td>Sheet thường (txt)</td><td>500đ / khuông</td><td>-</td></tr>
                        <tr><td>Sheet số (nber)</td><td>750đ / khuông</td><td>Cọc 10.000đ</td></tr>
                        <tr><td>Cảm âm</td><td>1.000đ / khuông</td><td>Cọc 20.000đ</td></tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            st.caption("⚠️ *Đối với Cảm âm, Foxy sẽ báo giá chính xác sau khi hoàn thành.*")

        # --- NÚT MẠNG XÃ HỘI ---
        st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<a href="https://www.facebook.com/foxy.ceo.o" target="_blank" style="display:block; text-align:center; padding:10px; background:#1877F2; color:white; border-radius:8px; text-decoration:none; font-weight:bold;"><i class="fab fa-facebook"></i> Facebook</a>', unsafe_allow_html=True)
        with c2: st.markdown('<a href="https://www.youtube.com/@foxy.ceo.o" target="_blank" style="display:block; text-align:center; padding:10px; background:#FF0000; color:white; border-radius:8px; text-decoration:none; font-weight:bold;"><i class="fab fa-youtube"></i> YouTube</a>', unsafe_allow_html=True)
        with c3: st.markdown('<a href="https://www.tiktok.com/@foxy.ceo.o" target="_blank" style="display:block; text-align:center; padding:10px; background:#000000; color:white; border-radius:8px; text-decoration:none; font-weight:bold;"><i class="fab fa-tiktok"></i> TikTok</a>', unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- BỘ LỌC DẠNG TAB ---
        categories = ["all", "event", "free", "txt", "nber", "upd"]
        tabs = st.tabs([cat.upper() for cat in categories])
        
        tab_data = {cat: df.copy() for cat in categories}
        for cat in categories:
            if cat != "all":
                tab_data[cat] = df[df['Loại'] == cat]

        for i, tab in enumerate(tabs):
            cat = categories[i]
            with tab:
                search = st.text_input(f"Tìm tên bài hát trong mục {cat.upper()}...", key=f"search_{cat}")
                current_df = tab_data[cat]
                if search:
                    current_df = current_df[current_df['Tên nhạc'].astype(str).str.contains(search, case=False, na=False)]
                
                for _, row in current_df.iterrows():
                    ten_nhac = str(row.get('Tên nhạc', 'Không tên')).replace('*', '')
                    casi = row.get('Ca sĩ / nhạc sĩ', 'N/A')
                    trans = row.get('Transcripted', 'N/A')
                    upd = row.get('Upd', 'N/A')
                    gia = str(row.get('VND', '0')).strip()
                    download_url = str(row.get('Download', '')).strip()
                    test_url = str(row.get('Test', '')).strip()
                    
                    is_dl = download_url.lower().startswith('http')
                    is_test = test_url.lower().startswith('http')
                    is_anchor = download_url.strip() == "#top"

                    btn_label = f'Liên hệ mua: {gia} VND' if not is_dl or is_anchor else 'Tải về'
                    btn_link = download_url if (is_dl and not is_anchor) else "#top"

                    st.markdown(f'<h3 style="font-size: 20px; margin: 5px 0;">{ten_nhac}</h3>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size: 14px; color: #555;">🎤 {casi} | ✍️ Trans: {trans} | 📅 Upd: {upd}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'''
                        <div style="display: flex; gap: 5px; margin-top: 5px; margin-bottom: 10px;">
                            <a href="{test_url if is_test else '#'}" target="_blank" style="flex:1; text-decoration:none;">
                                <button style="width:100%; border:none; padding:8px; background:{'#FF0000' if is_test else '#ddd'}; color:white; border-radius:5px;">▶</button>
                            </a>
                            <a href="{btn_link}" target="{"_blank" if not is_anchor else "_self"}" style="flex:3; text-decoration:none;">
                                <button style="width:100%; border:none; padding:8px; background:#00008C; color:white; border-radius:5px;">{btn_label}</button>
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.markdown('<hr style="margin:5px 0;">', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Đã có lỗi xảy ra: {e}")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

# --- CSS CẤU HÌNH CHUNG ---
st.markdown("""
    <style>
        /* Ẩn icon liên kết (cái xích) của tiêu đề */
        button[aria-label="Link"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ... (các phần code còn lại của cậu)
# 1. Cấu hình trang
st.set_page_config(page_title="Kho Sheet Nhạc", layout="centered")

# URL Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsybhqY890uEGLVqXyvC9Ovlfi-eXjjiIQ0jLMVDGc1TIaimWkLmT6F7RlI5DsWg/pub?gid=1844334473&single=true&output=csv"

# 2. Hàm load dữ liệu tối ưu hơn
@st.cache_data(ttl=60) # Tăng lên 60s để giảm tải cho Google
def load_data():
    try:
        # Thêm header=0 nếu file của cậu đã chuẩn dòng đầu là tiêu đề
        # Nếu chưa chuẩn, đoạn code lọc dòng bên dưới của cậu là đúng rồi
        df = pd.read_csv(SHEET_URL)
        
        # Làm sạch cột (Loại bỏ khoảng trắng dư thừa)
        df.columns = df.columns.str.strip()
        
        # Nếu cậu cần lọc dòng header như cũ:
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
        return pd.DataFrame() # Trả về df rỗng nếu lỗi

# 3. Main Logic
try:
    with st.spinner("Đang tải dữ liệu..."):
        df = load_data()
        
    if df.empty:
        st.error("Không thể tải được dữ liệu từ Google Sheet. Kiểm tra lại đường truyền hoặc link nhé!")
    else:
        st.title("🎵 Kho Sheet Nhạc")
        
        tab_filter = st.radio("Chọn xem:", ["all","event","free","txt","nber"], horizontal=True)
        filtered_df = df.copy()
        
        if tab_filter != "all":
            filtered_df = filtered_df[filtered_df['Loại'] == tab_filter]

        search = st.text_input("🔍 Tìm tên bài hát...")
        if search:
            filtered_df = filtered_df[filtered_df['Tên nhạc'].astype(str).str.contains(search, case=False, na=False)]

        # Đường kẻ ngang phía trên nếu cần
        st.markdown("---")

    for index, row in filtered_df.iterrows():
        # ... các biến ten_nhac, casi, trans ...
        
        # 1. Tên nhạc: ép margin bằng 0
        st.markdown(f'<h3 style="font-size: 24px; margin: 0px;">{ten_nhac}</h3>', unsafe_allow_html=True)
        
        # 2. Tác giả: ép margin bằng 0
        st.markdown(f'<div style="font-size: 15px; font-weight: bold; color: #555; margin: 0px;">🎤 {casi} | ✍️ Trans: {trans}</div>', unsafe_allow_html=True)
        
        # 3. Khối nút: ép margin trên/dưới bằng 0
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
        
        # 4. Đường kẻ: ép margin bằng 0 để nó nằm sát ngay dưới nút
        st.markdown('<hr style="margin: 5px 0px; border: 0; border-top: 1px solid #ccc;">', unsafe_allow_html=True)
        
        # Đường kẻ ngang phía dưới
        st.markdown("---")

except Exception as e:
    st.error(f"Đã có lỗi xảy ra: {e}")

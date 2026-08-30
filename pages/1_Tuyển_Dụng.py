import base64
import os
import streamlit as st

st.set_page_config(
    page_title="Thông Tin Tuyển Dụng - JLPT Reader",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.job-page-container {
    max-width: 820px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 14px;
    padding: 26px 32px;
    border: 1px solid #ffccd5;
    box-shadow: 0 4px 20px rgba(216, 27, 96, 0.08);
    font-family: 'Segoe UI', Arial, sans-serif;
}
.job-header {
    text-align: center;
    border-bottom: 2px dashed #ff80ab;
    padding-bottom: 20px;
    margin-bottom: 25px;
}
.job-title {
    color: #d81b60;
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 8px;
}
.job-sub {
    color: #555;
    font-size: 0.98rem;
    line-height: 1.5;
}
.badge-pill-list {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.badge-pill {
    background: #ffebee;
    color: #c2185b;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
}
.section-head {
    color: #d81b60;
    font-size: 1.25rem;
    font-weight: 700;
    margin: 26px 0 14px 0;
}
.job-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}
@media (max-width: 650px) {
    .job-grid-2x2 { grid-template-columns: 1fr; }
}
.job-item-card {
    background: #fffafb;
    border: 1px solid #ffd1dc;
    border-left: 5px solid #d81b60;
    padding: 14px 16px;
    border-radius: 8px;
}
.job-item-card h4 {
    color: #c2185b;
    margin-bottom: 8px;
    font-size: 1rem;
    font-weight: 700;
}
.job-item-card ul {
    padding-left: 18px;
    font-size: 0.88rem;
    color: #444;
    line-height: 1.5;
}
.benefits-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    list-style: none;
    padding: 0;
    margin: 0;
}
@media (max-width: 650px) {
    .benefits-grid { grid-template-columns: 1fr; }
}
.benefits-grid li {
    background: #f8fff8;
    border: 1px solid #c8e6c9;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.88rem;
    color: #2e7d32;
    font-weight: 600;
}
.contact-box-wrapper {
    margin-top: 30px;
    background: linear-gradient(135deg, #fff0f3, #ffe4e8);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
    border: 1px dashed #ff80ab;
}
.contact-box-wrapper img {
    width: 140px;
    height: 140px;
    border-radius: 8px;
    background: #ffffff;
    padding: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.back-btn-link {
    display: inline-block;
    margin-bottom: 15px;
    color: #d81b60;
    text-decoration: none;
    font-weight: 700;
    font-size: 0.95rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# Đọc mã QR Zalo
qr_b64_src = ""
for img_name in ["zalo_qr.png", "zalo_qr.jpg", "zalo_qr.jpeg"]:
    if os.path.exists(img_name):
        with open(img_name, "rb") as qrf:
            qr_b64_src = f"data:image/png;base64,{base64.b64encode(qrf.read()).decode()}"
        break

if not qr_b64_src:
    qr_b64_src = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://zalo.me"

html_body = f"""
<a href="/" target="_self" class="back-btn-link">⬅ Quay lại Trang Luyện Đọc Tiếng Nhật</a>

<div class="job-page-container">
<div class="job-header">
<h1 class="job-title">🔥 N3+ BẮT ĐẦU SỰ NGHIỆP ĐÚNG CHUYÊN MÔN</h1>
<p class="job-sub">Bạn học Kiến trúc / Xây dựng, có tiếng Nhật N3 trở lên, đang tìm một công việc không yêu cầu kinh nghiệm nhưng được đào tạo bài bản?</p>
<div class="badge-pill-list">
<span class="badge-pill">🎯 16 Vị trí</span>
<span class="badge-pill">📍 Đống Đa, Hà Nội</span>
<span class="badge-pill">🚀 Đi làm: Đầu T10/2026</span>
</div>
</div>

<div class="section-head">📌 4 Hướng Công Việc Theo Thế Mạnh</div>
<div class="job-grid-2x2">
<div class="job-item-card">
<h4>🏠 THIẾT KẾ KIẾN TRÚC NHÀ Ở (09 vị trí)</h4>
<ul>
<li>Tiếng Nhật N3+</li>
<li>~12 triệu Gross</li>
<li>Kiểm tra, hiệu chỉnh bản vẽ nhà ở lắp ghép theo tiêu chuẩn Nhật Bản</li>
</ul>
</div>
<div class="job-item-card">
<h4>📐 XỬ LÝ SỐ LIỆU BẢN VẼ (02 vị trí)</h4>
<ul>
<li>Tiếng Nhật N3+ (Ưu tiên biết AutoCAD)</li>
<li>~12 triệu Gross</li>
<li>Chỉnh sửa bản vẽ chi tiết theo yêu cầu khách hàng</li>
</ul>
</div>
<div class="job-item-card">
<h4>🧮 TÍNH TOÁN NGUYÊN VẬT LIỆU (02 vị trí)</h4>
<ul>
<li>Tiếng Nhật N3+</li>
<li>~12 triệu Gross</li>
<li>Bóc tách & tính toán vật liệu từ dữ liệu thiết kế Nhật Bản</li>
</ul>
</div>
<div class="job-item-card">
<h4>💻 BIM KIẾN TRÚC (03 vị trí)</h4>
<ul>
<li>N2+ hoặc N3 + nền tảng kỹ thuật</li>
<li>Lương thỏa thuận</li>
<li>Dựng mô hình 3D, triển khai bản vẽ BIM; cơ hội tham gia phiên/biên dịch</li>
</ul>
</div>
</div>

<div class="section-head">✨ Quyền Lợi & Đãi Ngộ Nổi Bật</div>
<ul class="benefits-grid">
<li>✅ Không yêu cầu kinh nghiệm</li>
<li>✅ Tốt nghiệp ĐH / CĐ / Senmon</li>
<li>✅ Được đào tạo bài bản sau khi vào làm</li>
<li>✅ Thưởng tháng 13 + thưởng đặc biệt cuối năm</li>
<li>✅ Thưởng kinh doanh + lương OT đầy đủ</li>
<li>✅ Hỗ trợ chi phí học tiếng Nhật</li>
<li>✅ Cơ hội đào tạo / công tác tại Nhật Bản</li>
<li>✅ Đầy đủ BHXH, BHYT + khám sức khỏe</li>
<li>✅ Làm việc: T2 – T6 (8:00 – 17:00, nghỉ T7-CN)</li>
</ul>

<div class="contact-box-wrapper">
<img src="{qr_b64_src}" alt="QR Zalo Hân Nguyễn">
<div style="flex: 1;">
<h3 style="color: #d81b60; margin: 0 0 6px 0;">📲 Liên hệ: Hân Nguyễn (HR)</h3>
<p style="font-size: 0.9rem; color: #555; margin: 0 0 8px 0;">Quét mã QR Zalo bên cạnh để gửi CV hoặc nhận tư vấn chi tiết về từng vị trí.</p>
<div style="color: #c2185b; font-weight: bold; font-size: 0.95rem;">⏰ Hạn nhận CV: 11/09/2026</div>
<div style="color: #c2185b; font-weight: bold; font-size: 0.95rem;">🚀 Dự kiến đi làm: Đầu tháng 10/2026</div>
</div>
</div>
</div>
"""

st.markdown(html_body, unsafe_allow_html=True)

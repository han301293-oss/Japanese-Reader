import base64
import os
import streamlit as st

st.set_page_config(
    page_title="Thông Tin Tuyển Dụng - DAIWAHOUSE VIỆT NAM",
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
    background: #ffffff !important;
    border-radius: 14px;
    padding: 24px 20px;
    border: 1px solid #ffccd5;
    box-shadow: 0 4px 20px rgba(216, 27, 96, 0.08);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333333 !important;
}
.company-badge {
    display: inline-block;
    background: #ffebee !important;
    color: #d81b60 !important;
    font-size: 0.88rem;
    font-weight: 800;
    padding: 4px 14px;
    border-radius: 6px;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
    border: 1px solid #ffccd5;
}
.job-header {
    text-align: center;
    border-bottom: 2px dashed #ff80ab;
    padding-bottom: 20px;
    margin-bottom: 25px;
}
.job-title {
    color: #d81b60 !important;
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
    line-height: 1.4 !important;
    display: block !important;
}
.job-subtitle {
    display: block !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #c2185b !important;
    margin-top: 4px;
}
.job-sub {
    color: #444444 !important;
    font-size: 0.95rem !important;
    line-height: 1.5;
}
.badge-pill-list {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.badge-pill {
    background: #ffebee !important;
    color: #c2185b !important;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.82rem;
}
.section-head {
    color: #d81b60 !important;
    font-size: 1.18rem !important;
    font-weight: 700 !important;
    margin: 24px 0 14px 0;
}
.job-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}
@media (max-width: 650px) {
    .job-grid-2x2 { grid-template-columns: 1fr; }
    .job-page-container { padding: 18px 14px; }
    .job-title { font-size: 1.25rem !important; }
}
.job-item-card {
    background: #fffafb !important;
    border: 1px solid #ffd1dc;
    border-left: 5px solid #d81b60;
    padding: 14px 16px;
    border-radius: 8px;
}
.job-item-card h4 {
    color: #c2185b !important;
    margin-bottom: 8px;
    font-size: 0.98rem !important;
    font-weight: 700 !important;
}
.job-item-card ul {
    padding-left: 18px;
    font-size: 0.88rem !important;
    color: #444444 !important;
    line-height: 1.5;
    margin: 0;
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
    background: #f8fff8 !important;
    border: 1px solid #c8e6c9;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.88rem !important;
    color: #2e7d32 !important;
    font-weight: 600;
}
.contact-box-wrapper {
    margin-top: 26px;
    background: linear-gradient(135deg, #fff0f3, #ffe4e8) !important;
    border-radius: 12px;
    padding: 18px;
    display: flex;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
    border: 1px dashed #ff80ab;
}
.contact-box-wrapper img {
    width: 130px;
    height: 130px;
    border-radius: 8px;
    background: #ffffff !important;
    padding: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.contact-link {
    color: #0d47a1 !important;
    font-weight: 700;
    text-decoration: none;
}
.back-btn-link {
    display: inline-block;
    margin-bottom: 15px;
    color: #d81b60 !important;
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
<div class="company-badge">🏢 DAIWAHOUSE VIỆT NAM</div>
<div class="job-title">🔥 TUYỂN DỤNG 16 NHÂN VIÊN TIẾNG NHẬT N3+</div>
<div class="job-subtitle">(Không yêu cầu kinh nghiệm)</div>
<p class="job-sub" style="margin-top: 10px;">Bạn học Kiến trúc / Xây dựng hoặc 1 một chuyên ngành kĩ thuật khác, có tiếng Nhật N3 trở lên, đang tìm một công việc không yêu cầu kinh nghiệm nhưng được đào tạo bài bản?</p>
<div class="badge-pill-list">
<span class="badge-pill">🎯 16 Vị trí</span>
<span class="badge-pill">📍 Đống Đa, Hà Nội</span>
<span class="badge-pill">🚀 Đi làm: Đầu T10/2026</span>
</div>
</div>

<div class="section-head">📌 Vị trí công việc đang tuyển dụng:</div>
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
<li>✅ Thưởng tháng 13 + thưởng đặc biệt cuối năm (1-2 tháng lương)</li>
<li>✅ Thưởng kinh doanh + lương OT đầy đủ</li>
<li>✅ Hỗ trợ chi phí học tiếng Nhật</li>
<li>✅ Cơ hội đào tạo / công tác tại Nhật Bản</li>
<li>✅ Đầy đủ BHXH, BHYT + khám sức khỏe</li>
<li>✅ Làm việc: T2 – T6 (8:00 – 17:00, nghỉ T7-CN)</li>
</ul>

<div class="contact-box-wrapper">
<img src="{qr_b64_src}" alt="QR Zalo Hân Nguyễn">
<div style="flex: 1;">
<h3 style="color: #d81b60 !important; margin: 0 0 6px 0;">📲 Liên hệ: Hân Nguyễn (HR)</h3>
<p style="font-size: 0.9rem; color: #444444 !important; margin: 0 0 6px 0;">📧 Email: <a href="mailto:nguyenthihan@daiwahouse.vn" class="contact-link">nguyenthihan@daiwahouse.vn</a></p>
<p style="font-size: 0.88rem; color: #555555 !important; margin: 0 0 8px 0;">Quét mã QR Zalo bên cạnh để gửi CV hoặc nhận tư vấn chi tiết về từng vị trí.</p>
<div style="color: #c2185b !important; font-weight: bold; font-size: 0.95rem;">⏰ Hạn nhận CV: 11/09/2026</div>
<div style="color: #c2185b !important; font-weight: bold; font-size: 0.95rem;">🚀 Dự kiến đi làm: Đầu tháng 10/2026</div>
</div>
</div>
</div>
"""

st.markdown(html_body, unsafe_allow_html=True)

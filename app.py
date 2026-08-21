import streamlit as st
import google.generativeai as genai
import json
import io
import re
import base64
import pandas as pd

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

st.set_page_config(
    page_title="Luyện Đọc & Phân Tích Tiếng Nhật JLPT Pro",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cấu hình CSS tùy biến: Nâng cấp Typography chuẩn Nhật Bản & tối ưu giao diện
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.95), rgba(255, 228, 238, 0.95)) !important;
        border-bottom: 1px solid #ffd1dc !important;
        box-shadow: 0 2px 10px rgba(255, 182, 193, 0.25) !important;
        backdrop-filter: blur(8px) !important;
        z-index: 999990 !important;
    }
    @media (prefers-color-scheme: dark) {
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, rgba(40, 18, 28, 0.95), rgba(30, 12, 22, 0.95)) !important;
            border-bottom: 1px solid #5a2a3a !important;
            box-shadow: 0 2px 10px rgba(255, 117, 140, 0.2) !important;
        }
    }

    .app-title-fixed {
        position: fixed;
        top: 6px;
        left: 20px;
        z-index: 999999;
        pointer-events: none;
    }
    .app-main-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #d81b60 !important;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .app-sub-title {
        font-size: 0.78rem;
        color: #666 !important;
        margin: 0;
    }
    @media (prefers-color-scheme: dark) {
        .app-main-title { color: #ff80ab !important; }
        .app-sub-title { color: #bbb !important; }
    }

    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 3rem !important;
    }

    .reader-paragraph-card {
        background-color: #ffffff;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #f0eae1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    @media (prefers-color-scheme: dark) {
        .reader-paragraph-card {
            background-color: #231d24;
            border-color: #4a3443;
        }
    }

    .jp-text-line {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 1.3rem;
        line-height: 2.8rem;
        color: #2c3e50;
        letter-spacing: 0.04em;
    }
    @media (prefers-color-scheme: dark) {
        .jp-text-line {
            color: #f1e7ea;
        }
    }

    ruby {
        ruby-position: over;
        font-family: 'Noto Sans JP', sans-serif;
    }
    rt {
        font-size: 0.58em;
        color: #e91e63;
        font-weight: 600;
        user-select: none;
    }

    .vi-translation-box {
        background: rgba(255, 243, 224, 0.85);
        border-left: 4px solid #ff9800;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 14px;
        font-size: 1.05rem;
        font-weight: 500;
        color: #d84315;
        line-height: 1.6rem;
    }
    @media (prefers-color-scheme: dark) {
        .vi-translation-box {
            background: rgba(60, 40, 20, 0.85);
            border-left: 4px solid #ffb74d;
            color: #ffe0b2;
        }
    }

    .resource-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e9ecef;
    }
    @media (prefers-color-scheme: dark) {
        .resource-box {
            background-color: #2b262d;
            border-color: #423b45;
        }
    }

    .sakura-container {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        z-index: 999;
        overflow: hidden;
    }
    .petal {
        position: absolute;
        background-color: #ffb7c5;
        border-radius: 150% 0 150% 0;
        opacity: 0.7;
        animation: fall 10s linear infinite, sway 3s ease-in-out infinite alternate;
    }
    .petal:nth-child(1) { left: 5%; width: 12px; height: 14px; animation-duration: 9s, 3s; animation-delay: 0s; }
    .petal:nth-child(2) { left: 18%; width: 14px; height: 16px; animation-duration: 11s, 4s; animation-delay: 1.5s; opacity: 0.6; }
    .petal:nth-child(3) { left: 32%; width: 10px; height: 12px; animation-duration: 8s, 2.5s; animation-delay: 3s; }
    .petal:nth-child(4) { left: 45%; width: 15px; height: 17px; animation-duration: 12s, 3.5s; animation-delay: 0.5s; opacity: 0.5; }
    .petal:nth-child(5) { left: 58%; width: 11px; height: 13px; animation-duration: 10s, 3s; animation-delay: 2s; }
    .petal:nth-child(6) { left: 72%; width: 13px; height: 15px; animation-duration: 9.5s, 4s; animation-delay: 4s; opacity: 0.65; }
    .petal:nth-child(7) { left: 85%; width: 12px; height: 14px; animation-duration: 11.5s, 3s; animation-delay: 1s; }
    .petal:nth-child(8) { left: 95%; width: 14px; height: 16px; animation-duration: 8.5s, 2.8s; animation-delay: 2.5s; }

    @keyframes fall { 0% { top: -20px; transform: rotate(0deg); } 100% { top: 100vh; transform: rotate(360deg); } }
    @keyframes sway { 0% { transform: translateX(0px) rotate(0deg); } 100% { transform: translateX(35px) rotate(45deg); } }
</style>

<div class="sakura-container">
    <div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div>
    <div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div>
</div>

<div class="app-title-fixed">
    <div class="app-main-title">🌸 Japanese Reader Pro</div>
    <div class="app-sub-title">Luyện đọc hiểu thông minh • Tra cứu Furigana • Phân tích ngữ pháp & Tạo đề JLPT</div>
</div>
""", unsafe_allow_html=True)

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key:", type="password")

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "current_user_text" not in st.session_state:
    st.session_state.current_user_text = ""
if "raw_audio_b64" not in st.session_state:
    st.session_state.raw_audio_b64 = None

# Giao diện 2 cột
col_left, col_right = st.columns([6.8, 3.2], gap="medium")

with col_left:
    user_text = st.text_area(
        "📋 Dán bài đọc tiếng Nhật vào đây:",
        height=220,
        placeholder="Dán bài báo, truyện ngắn hoặc đoạn văn tiếng Nhật vào đây..."
    )
    analyze_btn = st.button("🚀 Bắt đầu Phân tích & Tạo bài học", type="primary", use_container_width=True)

with col_right:
    st.markdown('<div class="resource-box">', unsafe_allow_html=True)
    st.markdown("#### 🌐 Nguồn bài đọc tiếng Nhật uy tín")
    st.caption("Copy bài viết từ các trang sau và dán sang ô bên trái:")

    with st.expander("🟢 Sơ cấp (N5 - N4)", expanded=True):
        st.markdown("""
        * 📰 [NHK News Easy](https://www3.nhk.or.jp/news/easy/): Tin tức tiếng Nhật đơn giản có Furigana.
        * 📖 [Tadoku Graded Readers](https://tadoku.org/japanese/free-books/): Sách truyện ngắn chia theo cấp độ.
        * 🧒 [Hukumusume Fairy Tales](http://hukumusume.com/douwa/): Truyện cổ tích thiếu nhi Nhật Bản.
        """)

    with st.expander("🟡 Trung cấp (N3 - N2)"):
        st.markdown("""
        * 📰 [Watanoc](http://watanoc.com/): Tạp chí văn hóa viết bằng tiếng Nhật dễ hiểu.
        * 📰 [Mainichi Shimbun (Thiếu nhi)](https://mainichi.jp/maisho/): Báo học sinh Nhật Bản.
        * 📝 [Note.com](https://note.com/): Blog và tản văn của người bản xứ.
        """)

    with st.expander("🔴 Cao cấp (N1 & Báo chí thực tế)"):
        st.markdown("""
        * 🗞️ [Asahi Shimbun (朝日新聞)](https://www.asahi.com/): Báo xã luận chính luận chuyên sâu.
        * 🗞️ [Yahoo Japan News](https://news.yahoo.co.jp/): Tin tức đời sống nóng hổi.
        * 📚 [Aozora Bunko (青空文庫)](https://www.aozora.gr.jp/): Kho văn học cổ điển Nhật Bản.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

SYSTEM_PROMPT = """
Bạn là giáo viên tiếng Nhật JLPT chuyên nghiệp. Hãy phân tích đoạn văn tiếng Nhật được cung cấp và trả về kết quả định dạng JSON thuần túy theo mẫu sau:

{
  "summary": {
    "estimated_jlpt_level": "N3",
    "topic": "Chủ đề bài viết",
    "word_count": 120
  },
  "paragraphs": [
    {
      "original_text": "Đoạn văn tiếng Nhật gốc",
      "furigana_html": "Đoạn văn có gắn thẻ <ruby>Chữ Hán<rt>cách đọc</rt></ruby>",
      "vietnamese_translation": "Bản dịch tiếng Việt chuẩn xác"
    }
  ],
  "grammar_analysis": [
    {
      "pattern": "Mẫu ngữ pháp",
      "jlpt_level": "N3",
      "meaning": "Ý nghĩa",
      "usage_in_text": "Câu ví dụ trong bài",
      "explanation": "Giải thích chi tiết"
    }
  ],
  "vocabulary_list": [
    {
      "word": "Từ vựng",
      "reading": "Cách đọc Hiragana",
      "part_of_speech": "Từ loại",
      "jlpt_level": "N3",
      "vietnamese_meaning": "Nghĩa tiếng Việt"
    }
  ],
  "kanji_list": [
    {
      "kanji": "Hán tự",
      "han_viet": "Âm Hán Việt",
      "jlpt_level": "N3",
      "onyomi": "Âm On",
      "kunyomi": "Âm Kun",
      "meaning": "Ý nghĩa"
    }
  ],
  "jlpt_practice_questions": [
    {
      "question_number": 1,
      "question_text": "Câu hỏi JLPT bằng tiếng Nhật",
      "question_vietnamese": "Dịch câu hỏi",
      "options": {
        "A": "Lựa chọn A",
        "B": "Lựa chọn B",
        "C": "Lựa chọn C",
        "D": "Lựa chọn D"
      },
      "correct_answer": "A",
      "option_analysis": {
        "A": "Giải thích",
        "B": "Giải thích",
        "C": "Giải thích",
        "D": "Giải thích"
      }
    }
  ]
}

Hãy tạo 3 đến 5 câu hỏi trắc nghiệm đọc hiểu hay nhất. Chỉ trả về chuỗi JSON hợp lệ.
"""

def clean_and_parse_json(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text, strict=False)
    except Exception:
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group(0) not in ['\n', '\r', '\t'] else m.group(0), text)
        return json.loads(cleaned, strict=False)

if analyze_btn:
    if not api_key:
        st.error("⚠️ Vui lòng cung cấp Gemini API Key để tiếp tục.")
    elif not user_text.strip():
        st.warning("⚠️ Vui lòng nhập nội dung bài đọc.")
    else:
        with st.status("🌸 Đang xử lý bài học...", expanded=True) as status:
            try:
                st.write("🧠 AI đang phân tích bài đọc...")
                genai.configure(api_key=api_key)
                
                model = genai.GenerativeModel(
                    model_name="gemini-3.6-flash",
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.2
                    }
                )
                
                prompt_content = f"{SYSTEM_PROMPT}\n\nĐoạn văn tiếng Nhật cần phân tích:\n{user_text}"
                response = model.generate_content(prompt_content)
                st.session_state.analysis_data = clean_and_parse_json(response.text)
                st.session_state.current_user_text = user_text

                st.write("🎙️ Đang tạo bản thu âm phát âm AI...")
                if TTS_AVAILABLE:
                    try:
                        audio_text = user_text[:600]
                        tts = gTTS(text=audio_text, lang='ja', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.session_state.raw_audio_b64 = base64.b64encode(fp.read()).decode()
                    except Exception:
                        st.session_state.raw_audio_b64 = None
                
                status.update(label="🎉 Phân tích hoàn tất thành công!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="❌ Có lỗi xảy ra!", state="error", expanded=True)
                st.error(f"Chi tiết lỗi: {str(e)}")

# HIỂN THỊ KẾT QUẢ
if st.session_state.analysis_data:
    data = st.session_state.analysis_data

    sum_col1, sum_col2 = st.columns(2)
    sum_col1.info(f"🏷️ **Cấp độ ước tính:** {data.get('summary', {}).get('estimated_jlpt_level', 'N/A')}")
    sum_col2.info(f"📖 **Chủ đề:** {data.get('summary', {}).get('topic', 'Chung')}")

    tab_read, tab_grammar, tab_vocab, tab_kanji, tab_quiz = st.tabs([
        "📖 Trình Đọc & Dịch", "📝 Ngữ pháp", "📚 Từ vựng & Flashcard", "🈲 Hán tự (Kanji)", "❓ Câu hỏi Luyện thi JLPT"
    ])

    # Tab 1: Đọc & Dịch
    with tab

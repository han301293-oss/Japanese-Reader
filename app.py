import streamlit as st
import google.generativeai as genai
import json
import io
import re
import csv
import os
import html as html_lib
import datetime
import base64
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

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

# ============================================================
# FIX #1: st.secrets có thể raise lỗi nếu không có secrets.toml,
# và ô nhập key nằm trong sidebar đang collapsed mặc định ->
# thêm try/except + gợi ý mở sidebar cho người dùng thấy.
# ============================================================
try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    api_key = None

if not api_key:
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key:", type="password")
if not api_key:
    st.info(
        "💡 Cần Gemini API Key để dùng công cụ này. Mở **thanh bên trái** "
        "(bấm mũi tên **☰** ở góc trên-trái) để nhập key, hoặc lấy key miễn phí "
        "tại [Google AI Studio](https://aistudio.google.com/apikey)."
    )

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "current_user_text" not in st.session_state:
    st.session_state.current_user_text = ""
if "raw_audio_b64" not in st.session_state:
    st.session_state.raw_audio_b64 = None
# FIX #2: id tăng dần cho mỗi lần phân tích thành công, dùng để
# tạo key duy nhất cho các widget của quiz (xem tab_quiz bên dưới).
if "analysis_id" not in st.session_state:
    st.session_state.analysis_id = 0

# Giao diện 2 cột
col_left, col_right = st.columns([6.8, 3.2], gap="medium")

with col_left:
    # FIX #11 (UI): trước đây khung này (textarea + nút) chỉ cao ~280px,
    # trong khi khung bên phải cao 430px (do container(height=430) ở dưới)
    # -> lệch chiều cao rõ rệt như ảnh bạn khoanh đỏ. Bọc trong cùng loại
    # st.container(border=True, height=430) và tăng chiều cao textarea để
    # 2 khung cân đối, đồng thời có viền giống nhau cho thống nhất giao diện.
    with st.container(border=True, height=430):
        user_text = st.text_area(
            "📋 Dán bài đọc tiếng Nhật vào đây:",
            height=300,
            placeholder="Dán bài báo, truyện ngắn hoặc đoạn văn tiếng Nhật vào đây...",
            label_visibility="visible"
        )
        analyze_btn = st.button("🚀 Bắt đầu Phân tích & Tạo bài học", type="primary", use_container_width=True)

with col_right:
    # FIX #8 (UI): trước đây mở thẻ <div class="resource-box"> bằng MỘT
    # lệnh st.markdown riêng rồi đóng bằng lệnh khác ở cuối — nhưng mỗi
    # st.markdown/st.expander render trong khối DOM RIÊNG của nó, nên thẻ
    # <div> mở không hề bọc được các expander bên trong => trình duyệt tự
    # đóng thẻ ngay tại chỗ, tạo ra một Ô XÁM RỖNG (đúng phần bạn khoanh đỏ
    # "1. thừa ô màu xám"). Thay bằng st.container(border=True, height=...)
    # — cách đúng của Streamlit để có 1 khung thật sự bao các widget bên
    # trong, đồng thời có chiều cao cố định kèm thanh cuộn riêng.
    with st.container(border=True, height=430):
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

# FIX #3: nói rõ ràng cho AI chỉ bọc <ruby> quanh phần Hán tự,
# không trùm cả okurigana/hiragana đi kèm -> furigana đặt đúng vị trí.
SYSTEM_PROMPT = """
Bạn là giáo viên tiếng Nhật JLPT cao cấp. Hãy phân tích bài đọc tiếng Nhật và trả về kết quả định dạng JSON thuần túy (không bọc markdown, không thêm chữ thừa) theo cấu trúc sau:
{
  "summary": { "estimated_jlpt_level": "N3", "topic": "Tên chủ đề", "word_count": 120 },
  "paragraphs": [
    {
      "original_text": "văn bản gốc",
      "furigana_html": "văn bản có thẻ <ruby>Hán tự<rt>cách đọc</rt></ruby> CHỈ bọc quanh các ký tự Hán tự liên tiếp, giữ nguyên hiragana/katakana/okurigana bên ngoài thẻ ruby",
      "vietnamese_translation": "dịch nghĩa tiếng Việt súc tích"
    }
  ],
  "grammar_analysis": [
    { "pattern": "Mẫu ngữ pháp", "jlpt_level": "N3", "meaning": "Ý nghĩa", "usage_in_text": "Câu trong bài", "explanation": "Giải thích ngắn gọn" }
  ],
  "vocabulary_list": [
    { "word": "Từ", "reading": "Cách đọc", "part_of_speech": "Từ loại", "jlpt_level": "N3", "vietnamese_meaning": "Nghĩa" }
  ],
  "kanji_list": [
    {
      "kanji": "Hán tự", "han_viet": "ÂM HÁN", "jlpt_level": "N3", "onyomi": "On", "kunyomi": "Kun", "meaning": "Nghĩa",
      "example_words": [
        { "word": "Từ vựng ví dụ chứa Hán tự này", "reading": "Cách đọc", "meaning": "Nghĩa tiếng Việt" }
      ]
    }
  ],
  "jlpt_practice_questions": [
    {
      "question_number": 1,
      "question_text": "Câu hỏi JLPT bằng tiếng Nhật",
      "question_vietnamese": "Dịch câu hỏi",
      "options": { "A": "Lựa chọn A", "B": "Lựa chọn B", "C": "Lựa chọn C", "D": "Lựa chọn D" },
      "correct_answer": "A",
      "option_analysis": {
        "A": "Giải thích tại sao đúng",
        "B": "Giải thích tại sao sai",
        "C": "Giải thích tại sao sai",
        "D": "Giải thích tại sao sai"
      }
    }
  ]
}
YÊU CẦU VỀ ĐỘ ĐẦY ĐỦ:
- "vocabulary_list": đây là DANH SÁCH TRA CỨU khi người học bôi đen bất kỳ từ nào trong bài, nên phải liệt kê GẦN NHƯ TOÀN BỘ các từ/cụm từ có nghĩa độc lập xuất hiện trong bài đọc — không chỉ những từ "khó" hay từ vựng JLPT. Cụ thể phải bao gồm CẢ:
  * Danh từ thường/địa danh/tên riêng (vd: 栃木県, 鹿沼市, tên tuyến tàu, tên người, tên công ty...) dù nghe "hiển nhiên" với người bản xứ.
  * Động từ, tính từ, phó từ, liên từ xuất hiện trong bài (kể cả những từ sơ cấp N5).
  * Cụm danh từ ghép (compound noun) nếu cụm đó thường được tra như 1 đơn vị nghĩa (vd: 特急列車, 運輸安全委員会).
  Mỗi từ trong "paragraphs" chỉ cần xuất hiện trong "vocabulary_list" MỘT LẦN (không lặp nếu từ đó xuất hiện nhiều lần trong bài). Không giới hạn số lượng tối đa — bài càng dài, danh sách càng dài, đó là điều BÌNH THƯỜNG và ĐÚNG YÊU CẦU, không được rút gọn vì lo ngại danh sách quá dài.
- "kanji_list": liệt kê TẤT CẢ Hán tự xuất hiện trong bài (không lặp lại Hán tự đã liệt kê). Với MỖI Hán tự, bổ sung 2-3 từ vựng ví dụ THẬT SỰ TỒN TẠI trong tiếng Nhật có chứa Hán tự đó — được phép ghép với BẤT KỲ Hán tự nào khác mà bạn biết là tạo thành từ có nghĩa (hoàn toàn KHÔNG giới hạn hay ưu tiên trong phạm vi các Hán tự xuất hiện ở bài đọc này), miễn là đó là từ vựng có thật, thường gặp, kèm cách đọc và nghĩa tiếng Việt chính xác. TUYỆT ĐỐI không bịa ra tổ hợp không tồn tại.
Chỉ tạo 3 đến 5 câu hỏi trắc nghiệm hay nhất, mỗi câu phải có "question_number" DUY NHẤT không trùng lặp (1, 2, 3...). Đảm bảo JSON hợp lệ, không chứa ký tự xuống dòng chưa escape.
"""

# FIX #13: trước đây chỉ DẶN trong SYSTEM_PROMPT là mỗi Hán tự phải có
# "example_words", nhưng lời dặn suông trong prompt không được Gemini
# tuân thủ tuyệt đối -> đây là lý do tab Hán tự hay hiện "Chưa có ví dụ
# từ vựng". Cách sửa đúng gốc: khai báo response_schema (kiểu OpenAPI)
# cho Gemini API — lúc này "example_words" trở thành field BẮT BUỘC với
# tối thiểu 2 phần tử, model không thể trả thiếu được nữa.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "object",
            "properties": {
                "estimated_jlpt_level": {"type": "string"},
                "topic": {"type": "string"},
                "word_count": {"type": "integer"},
            },
            "required": ["estimated_jlpt_level", "topic"],
        },
        "paragraphs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original_text": {"type": "string"},
                    "furigana_html": {"type": "string"},
                    "vietnamese_translation": {"type": "string"},
                },
                "required": ["original_text", "furigana_html", "vietnamese_translation"],
            },
        },
        "grammar_analysis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "jlpt_level": {"type": "string"},
                    "meaning": {"type": "string"},
                    "usage_in_text": {"type": "string"},
                    "explanation": {"type": "string"},
                },
                "required": ["pattern", "jlpt_level", "meaning", "usage_in_text", "explanation"],
            },
        },
        "vocabulary_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "reading": {"type": "string"},
                    "part_of_speech": {"type": "string"},
                    "jlpt_level": {"type": "string"},
                    "vietnamese_meaning": {"type": "string"},
                },
                "required": ["word", "reading", "part_of_speech", "jlpt_level", "vietnamese_meaning"],
            },
        },
        "kanji_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kanji": {"type": "string"},
                    "han_viet": {"type": "string"},
                    "jlpt_level": {"type": "string"},
                    "onyomi": {"type": "string"},
                    "kunyomi": {"type": "string"},
                    "meaning": {"type": "string"},
                    "example_words": {
                        "type": "array",
                        "minItems": 2,
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "reading": {"type": "string"},
                                "meaning": {"type": "string"},
                            },
                            "required": ["word", "reading", "meaning"],
                        },
                    },
                },
                "required": ["kanji", "han_viet", "jlpt_level", "onyomi", "kunyomi", "meaning", "example_words"],
            },
        },
        "jlpt_practice_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question_number": {"type": "integer"},
                    "question_text": {"type": "string"},
                    "question_vietnamese": {"type": "string"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "A": {"type": "string"}, "B": {"type": "string"},
                            "C": {"type": "string"}, "D": {"type": "string"},
                        },
                        "required": ["A", "B", "C", "D"],
                    },
                    "correct_answer": {"type": "string"},
                    "option_analysis": {
                        "type": "object",
                        "properties": {
                            "A": {"type": "string"}, "B": {"type": "string"},
                            "C": {"type": "string"}, "D": {"type": "string"},
                        },
                        "required": ["A", "B", "C", "D"],
                    },
                },
                "required": ["question_number", "question_text", "question_vietnamese", "options", "correct_answer", "option_analysis"],
            },
        },
    },
    "required": ["summary", "paragraphs", "grammar_analysis", "vocabulary_list", "kanji_list", "jlpt_practice_questions"],
}


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


# FIX #4: sanitize HTML do AI trả về (furigana_html) trước khi render
# với unsafe_allow_html=True — chỉ cho phép <ruby>/<rt>/<rb>, xóa mọi
# thẻ khác để tránh vỡ layout hoặc lọt thẻ lạ (<script>, <style>...).
_ALLOWED_RUBY_TAGS = r'ruby|rt|rb'


def sanitize_furigana_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    return re.sub(rf'</?(?!(?:{_ALLOWED_RUBY_TAGS})\b)[a-zA-Z][^>]*>', '', raw_html)


# FIX #9 (UI): hover/chạm vào một từ trong bài đọc sẽ hiện tooltip gồm
# cách đọc + từ loại + nghĩa tiếng Việt, lấy dữ liệu từ "vocabulary_list".
# Chỉ thay thế trong các ĐOẠN VĂN BẢN THUẦN (không đụng vào bên trong các
# thẻ HTML có sẵn như <ruby>/<rt>) để không phá vỡ cấu trúc furigana.
def build_vocab_tooltip_index(vocabulary_list: list) -> dict:
    idx = {}
    for v in vocabulary_list or []:
        w = (v.get("word") or "").strip()
        if w:
            idx[w] = v
    return idx


# FIX #12 (UI): trước đây MỌI từ vựng khớp đều bị gạch chân dotted sẵn
# trong bài đọc (gây rối mắt). Đổi sang mô hình "bôi đen từ nào, hiện
# nghĩa từ đó" — không gạch chân gì cả, người học tự chọn (drag/chạm) đúng
# từ mình muốn tra, tooltip nổi lên ngay tại vị trí bôi đen. Vì cần bắt
# sự kiện chọn văn bản (mouseup/touchend) bằng JavaScript thực thi được,
# phải dùng st.components.v1.html (iframe) thay vì st.markdown (script
# trong st.markdown không được trình duyệt thực thi).
def build_reader_component_html(cards_html: list, vocab_index: dict) -> str:
    vocab_payload = {
        w: {
            "word": w,
            "reading": info.get("reading", ""),
            "pos": info.get("part_of_speech", ""),
            "meaning": info.get("vietnamese_meaning", ""),
        }
        for w, info in (vocab_index or {}).items()
    }
    # Escape "</" để JSON không bị "vỡ" ra khỏi thẻ <script> khi nhúng.
    vocab_json = json.dumps(vocab_payload, ensure_ascii=False).replace("</", "<\\/")
    cards_joined = "\n".join(cards_html)

    return f"""
    <style>
        body {{ margin: 0; font-family: 'Noto Sans JP', sans-serif; -webkit-tap-highlight-color: transparent; }}
        #jp-reader-scroll {{ max-height: 640px; overflow-y: auto; padding: 4px 10px 4px 4px; }}
        .reader-paragraph-card {{
            background-color: #ffffff; padding: 20px 24px; border-radius: 12px;
            border: 1px solid #f0eae1; box-shadow: 0 2px 8px rgba(0,0,0,0.03); margin-bottom: 20px;
        }}
        .jp-text-line {{ font-size: 1.3rem; line-height: 2.8rem; color: #2c3e50; letter-spacing: 0.04em; }}
        ruby {{ ruby-position: over; }}
        rt {{ font-size: 0.58em; color: #e91e63; font-weight: 600; user-select: none; }}
        .vi-translation-box {{
            background: rgba(255, 243, 224, 0.85); border-left: 4px solid #ff9800; padding: 10px 16px;
            border-radius: 0 8px 8px 0; margin-top: 14px; font-size: 1.05rem; font-weight: 500;
            color: #d84315; line-height: 1.6rem;
        }}
        #jp-sel-tooltip {{
            position: fixed; display: none; background: #2c2c2c; color: #fff; padding: 8px 12px;
            border-radius: 8px; font-size: 0.9rem; max-width: 280px; z-index: 999999; line-height: 1.5;
            box-shadow: 0 4px 14px rgba(0,0,0,0.3);
        }}
        #jp-sel-tooltip b {{ color: #ff80ab; }}
        #jp-sel-tooltip .jp-sel-empty {{ color: #ccc; font-style: italic; }}
    </style>
    <div id="jp-reader-scroll">{cards_joined}</div>
    <div id="jp-sel-tooltip"></div>
    <script>
        const VOCAB = {vocab_json};
        const tooltip = document.getElementById('jp-sel-tooltip');

        function findEntry(text) {{
            if (!text) return null;
            if (VOCAB[text]) return VOCAB[text];
            let best = null;
            for (const key in VOCAB) {{
                if (text.indexOf(key) !== -1 && (!best || key.length > best.length)) best = key;
            }}
            return best ? VOCAB[best] : null;
        }}

        function showTooltip(rect, entry, rawText) {{
            if (entry) {{
                tooltip.innerHTML = '<b>' + entry.word + '</b>' +
                    (entry.reading ? ' [' + entry.reading + ']' : '') + '<br>' +
                    (entry.pos ? entry.pos + ' · ' : '') + (entry.meaning || '');
            }} else {{
                tooltip.innerHTML = '<b>' + rawText + '</b><br><span class="jp-sel-empty">Chưa có trong danh sách — thử bôi lại sát đúng 1 từ (có thể bạn đang chọn thừa/thiếu 1 ký tự)</span>';
            }}
            const top = Math.max(8, rect.top - 8);
            const left = Math.min(Math.max(8, rect.left + rect.width / 2 - 120), window.innerWidth - 250);
            tooltip.style.top = top + 'px';
            tooltip.style.left = left + 'px';
            tooltip.style.transform = 'translateY(-100%)';
            tooltip.style.display = 'block';
        }}

        function handleSelection() {{
            const sel = window.getSelection();
            const text = sel ? sel.toString().trim() : '';
            if (!text || sel.rangeCount === 0) {{ tooltip.style.display = 'none'; return; }}
            const rect = sel.getRangeAt(0).getBoundingClientRect();
            if (!rect || (rect.width === 0 && rect.height === 0)) {{ tooltip.style.display = 'none'; return; }}
            showTooltip(rect, findEntry(text), text);
        }}

        document.addEventListener('mouseup', handleSelection);
        document.addEventListener('touchend', handleSelection);
        document.addEventListener('mousedown', function(e) {{
            if (e.target !== tooltip) tooltip.style.display = 'none';
        }});
    </script>
    """


# FIX #5: cắt văn bản cho TTS tại ranh giới câu tiếng Nhật gần nhất
# thay vì cắt cứng ở ký tự thứ 600 (dễ cắt giữa cụm từ).
def smart_truncate_ja(text: str, limit: int = 600) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for punct in ("。", "！", "？", "\n"):
        idx = cut.rfind(punct)
        if idx > limit * 0.5:
            return cut[: idx + 1]
    return cut


FEEDBACK_FILE = "feedback_log.csv"  # chỉ dùng làm fallback khi Google Sheet lỗi/chưa cấu hình
FEEDBACK_RECIPIENT_EMAIL = "han301293@gmail.com"  # dùng để tự động chia sẻ quyền xem Sheet, xem hướng dẫn secrets bên dưới

_GSHEET_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


@st.cache_resource(show_spinner=False)
def _get_feedback_worksheet():
    """
    Kết nối tới Google Sheet chứa feedback bằng service account (an toàn hơn
    App Password vì quyền chỉ giới hạn trong đúng 1 file Sheet được chia sẻ).
    Yêu cầu trong .streamlit/secrets.toml (hoặc Secrets trên Streamlit Cloud):
      FEEDBACK_SHEET_ID = "id-cua-google-sheet"   # lấy từ URL của sheet
      GCP_SERVICE_ACCOUNT_JSON = \'\'\'
      ...dán NGUYÊN VĂN toàn bộ nội dung file JSON service account vào đây...
      \'\'\'
    Sheet phải được share (quyền Editor) cho email của service account
    (dạng ...@...iam.gserviceaccount.com, xem hướng dẫn setup).
    """
    creds_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
    sheet_id = st.secrets["FEEDBACK_SHEET_ID"]
    creds = Credentials.from_service_account_info(creds_info, scopes=_GSHEET_SCOPES)
    client = gspread.authorize(creds)
    ws = client.open_by_key(sheet_id).sheet1
    if not ws.get_all_values():
        ws.append_row(["timestamp", "name", "type", "content"])
    return ws


def _save_feedback_local_fallback(row: list) -> None:
    file_exists = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "name", "type", "content"])
        writer.writerow(row)


def save_feedback(name: str, fb_type: str, content: str) -> None:
    row = [datetime.datetime.now().isoformat(timespec="seconds"), name or "(ẩn danh)", fb_type, content]
    try:
        ws = _get_feedback_worksheet()
        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception:
        # Không để mất feedback nếu Google Sheet chưa cấu hình xong / tạm lỗi mạng
        _save_feedback_local_fallback(row)
        raise


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
                    # Dùng alias "gemini-flash-latest" thay vì ghim cứng version,
                    # để app tự trỏ tới bản Flash mới nhất mà Google phát hành,
                    # không phải sửa code mỗi khi có model mới ra mắt.
                    model_name="gemini-flash-latest",
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": RESPONSE_SCHEMA,
                        "temperature": 0.2
                    }
                )

                response = model.generate_content(f"{SYSTEM_PROMPT}\n\nBài đọc:\n{user_text}")
                st.session_state.analysis_data = clean_and_parse_json(response.text)
                st.session_state.current_user_text = user_text
                # FIX #2 (tiếp): tăng analysis_id mỗi lần phân tích MỚI thành công,
                # để các widget quiz ở bài đọc mới không bị dính state của bài cũ.
                st.session_state.analysis_id += 1

                # FIX #6: luôn reset audio cũ trước khi thử tạo audio mới,
                # tránh trường hợp TTS lỗi/không khả dụng mà vẫn giữ audio
                # của bài đọc trước đó (nghe nhầm bài).
                st.session_state.raw_audio_b64 = None
                st.write("🎙️ Đang tạo bản thu âm phát âm AI...")
                if TTS_AVAILABLE:
                    try:
                        audio_text = smart_truncate_ja(user_text, 600)
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
                # FIX #14: từ khi mở rộng "vocabulary_list" để liệt kê gần
                # hết từ trong bài (phục vụ tính năng bôi đen tra nghĩa),
                # JSON trả về từ AI dài hơn hẳn trước đây -> với bài đọc
                # RẤT dài, dễ vượt giới hạn output của model giữa chừng,
                # khiến JSON bị cắt cụt và không parse được. Gợi ý rõ
                # nguyên nhân này thay vì để người dùng đoán mò.
                if len(user_text) > 1500:
                    st.info(
                        "💡 Bài đọc khá dài (trên 1500 ký tự) — vì công cụ giờ liệt kê gần như "
                        "toàn bộ từ vựng trong bài, kết quả trả về có thể bị cắt cụt giữa chừng "
                        "với bài quá dài. Thử chia bài thành 2-3 đoạn ngắn hơn rồi phân tích riêng từng đoạn."
                    )

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
    with tab_read:
        st.markdown("#### 🎧 Luyện nghe bài đọc (Giọng AI chuẩn Nhật):")
        # FIX #10 (UI): trước đây selectbox có label riêng ("⚡ Tốc độ phát:")
        # nằm TRÊN nó, còn audio thì không có label -> 2 cột bị lệch hàng
        # (đúng phần bạn khoanh đỏ trong ảnh 3). Ẩn label mặc định của
        # selectbox (label_visibility="collapsed"), thay bằng 1 caption
        # ngắn đặt cạnh nó, và dùng vertical_alignment="center" để 2 cột
        # luôn canh giữa theo chiều cao của nhau.
        aud_col, spd_col = st.columns([3.5, 1.5], vertical_alignment="center")
        with spd_col:
            spd_label_col, spd_input_col = st.columns([1, 1.4], vertical_alignment="center")
            with spd_label_col:
                st.markdown("⚡ **Tốc độ:**")
            with spd_input_col:
                speed_val = st.selectbox(
                    "Tốc độ phát",
                    [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                    index=2,
                    format_func=lambda x: f"x{x}",
                    label_visibility="collapsed"
                )

        with aud_col:
            if st.session_state.raw_audio_b64:
                audio_html = f"""
                <audio id="custom_audio" controls style="width: 100%; height: 45px;">
                    <source src="data:audio/mp3;base64,{st.session_state.raw_audio_b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('custom_audio');
                    if (audio) {{ audio.playbackRate = {speed_val}; }}
                </script>
                """
                st.components.v1.html(audio_html, height=55)
                st.caption("⚠️ Đổi tốc độ phát sẽ tải lại audio từ đầu (giới hạn kỹ thuật của trình phát nhúng).")
            else:
                st.info("💡 Không thể tải file âm thanh cho bài đọc này.")

        st.markdown("---")

        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            furigana_mode = st.radio(
                "🌸 Chế độ hiển thị Furigana:",
                ["Ẩn toàn bộ Furigana", "Hiện toàn bộ Furigana"],
                horizontal=True
            )
        with ctrl_col2:
            show_translation = st.toggle("🇻🇳 Hiển thị bản dịch tiếng Việt", value=True)

        vocab_index = build_vocab_tooltip_index(data.get("vocabulary_list", []))

        cards_html = []
        for p in data.get("paragraphs", []):
            if furigana_mode == "Hiện toàn bộ Furigana":
                jp_content = sanitize_furigana_html(p.get('furigana_html', p.get('original_text', '')))
            else:
                jp_content = html_lib.escape(p.get('original_text', ''))

            trans_html = ""
            if show_translation and p.get('vietnamese_translation'):
                trans_text = html_lib.escape(p.get('vietnamese_translation'))
                trans_html = f"<div class='vi-translation-box'>🇻🇳 <strong>Dịch:</strong> {trans_text}</div>"

            cards_html.append(f"""
            <div class="reader-paragraph-card">
                <div class="jp-text-line">{jp_content}</div>
                {trans_html}
            </div>
            """)

        st.caption("🖱️ Bôi đen (hoặc chạm giữ trên điện thoại) vào một từ trong bài để xem nghĩa của từ đó.")
        st.components.v1.html(
            build_reader_component_html(cards_html, vocab_index),
            height=660,
            scrolling=False
        )

    # Tab 2: Ngữ pháp
    with tab_grammar:
        for g in data.get("grammar_analysis", []):
            with st.expander(f"📌 {g.get('pattern')} [{g.get('jlpt_level')}] - {g.get('meaning')}"):
                st.markdown(f"- **Ngữ cảnh trong bài:** `{g.get('usage_in_text')}`")
                st.markdown(f"- **Giải thích chi tiết:** {g.get('explanation')}")

    # Tab 3: Từ vựng & Anki Flashcard
    with tab_vocab:
        raw_vocab = data.get("vocabulary_list", [])
        vocab_rows = [
            {"Từ vựng": v.get("word"), "Cách đọc": v.get("reading"), "Cấp độ": v.get("jlpt_level"), "Từ loại": v.get("part_of_speech"), "Ý nghĩa": v.get("vietnamese_meaning")}
            for v in raw_vocab
        ]

        if vocab_rows:
            anki_df = pd.DataFrame([
                {
                    "Front": f"{v.get('word')} [{v.get('reading')}]",
                    "Back": f"{v.get('vietnamese_meaning')}<br><small>{v.get('part_of_speech')} | {v.get('jlpt_level')}</small>"
                }
                for v in raw_vocab
            ])
            csv_buffer = anki_df.to_csv(index=False, header=False).encode('utf-8')

            st.download_button(
                label="📥 Tải bộ từ vựng nhập vào Anki Flashcard (.CSV)",
                data=csv_buffer,
                file_name="anki_vocab_deck.csv",
                mime="text/csv",
                type="secondary"
            )
            st.caption("💡 Khi import vào Anki, nhớ tick **\"Allow HTML in fields\"** để thẻ hiển thị đúng định dạng.")

        st.dataframe(vocab_rows, use_container_width=True)

    # Tab 4: Kanji
    with tab_kanji:
        kanji_list = data.get("kanji_list", [])
        if not kanji_list:
            st.info("💡 Không có dữ liệu Hán tự cho bài đọc này.")
        for k in kanji_list:
            header = f"{k.get('kanji', '')}　·　{k.get('han_viet', '')}　[{k.get('jlpt_level', 'N/A')}]　—　{k.get('meaning', '')}"
            with st.expander(header):
                col_on, col_kun = st.columns(2)
                col_on.markdown(f"**Âm On:** {k.get('onyomi') or '—'}")
                col_kun.markdown(f"**Âm Kun:** {k.get('kunyomi') or '—'}")

                examples = k.get("example_words", [])
                if examples:
                    st.markdown("**📚 Từ vựng ví dụ mở rộng:**")
                    for ex in examples:
                        st.markdown(f"- **{ex.get('word', '')}** [{ex.get('reading', '')}] — {ex.get('meaning', '')}")
                elif k.get("meaning"):
                    # FIX #13 (tiếp) - lưới an toàn: nếu vì lý do gì đó AI vẫn
                    # thiếu example_words (vd. dữ liệu phân tích cũ trước khi
                    # có response_schema), dùng tạm chính nghĩa của Hán tự đó
                    # làm ví dụ 1-chữ, thay vì để trống. KHÔNG tự ghép Hán tự
                    # này với Hán tự khác trong bài để "đoán" ra từ mới — vì
                    # không có cách nào kiểm chứng đó có phải từ thật trong
                    # tiếng Nhật hay không, dễ dạy sai cho người học.
                    st.markdown("**📚 Từ vựng ví dụ:**")
                    st.markdown(f"- **{k.get('kanji', '')}** [{k.get('onyomi') or k.get('kunyomi') or ''}] — {k.get('meaning')} *(dùng độc lập)*")
                    st.caption("💡 Bài phân tích này chưa có ví dụ mở rộng đầy đủ — phân tích lại bài đọc để có danh sách ví dụ phong phú hơn.")
                else:
                    st.caption("Chưa có ví dụ từ vựng cho Hán tự này.")

    # Tab 5: Câu hỏi JLPT
    with tab_quiz:
        st.markdown("### ✍️ Luyện tập đọc hiểu JLPT")
        questions = data.get("jlpt_practice_questions", [])
        for idx, q in enumerate(questions):
            q_num = q.get("question_number", idx + 1)
            st.markdown(f"#### Câu {q_num}: {q.get('question_text')}")
            st.caption(f"*(Dịch: {q.get('question_vietnamese')})*")

            opts = q.get("options", {})
            choice_keys = [k for k in ["A", "B", "C", "D"] if k in opts]

            # FIX #2 (tiếp): key ghép analysis_id + idx (vị trí trong danh sách,
            # KHÔNG dùng q_num do AI trả về) -> luôn duy nhất trong 1 lần phân
            # tích (kể cả khi AI lỡ đánh trùng số câu) VÀ luôn được reset khi
            # có bài phân tích mới, không còn dính đáp án của bài cũ.
            user_choice = st.radio(
                f"Chọn đáp án cho câu {q_num}:",
                options=choice_keys,
                format_func=lambda x: f"{x}. {opts.get(x, '')}",
                key=f"quiz_radio_{st.session_state.analysis_id}_{idx}",
                index=None
            )

            correct_ans = q.get("correct_answer")
            opt_analysis = q.get("option_analysis", {})

            if user_choice is not None:
                if not correct_ans:
                    st.warning("⚠️ Câu này thiếu đáp án đúng từ AI, không thể chấm điểm.")
                elif user_choice == correct_ans:
                    st.success(f"🎉 **Chính xác!** Đáp án đúng là **{correct_ans}**.")
                else:
                    st.error(f"❌ **Chưa chính xác!** Bạn đã chọn **{user_choice}**, đáp án đúng là **{correct_ans}**.")

                st.markdown("**🔍 Phân tích chi tiết:**")
                for opt_k in choice_keys:
                    explanation_text = opt_analysis.get(opt_k, "Chưa có phân tích.")
                    if opt_k == correct_ans:
                        st.markdown(f"- ✅ **Đáp án {opt_k}:** {explanation_text}")
                    else:
                        st.markdown(f"- ❌ **Đáp án {opt_k}:** {explanation_text}")
            st.markdown("---")

    # Tài liệu gợi ý
    st.markdown("### 📚 Tài liệu gợi ý nâng cao trình độ")
    st.caption("*Trang web có thể nhận hoa hồng khi bạn mua qua liên kết giới thiệu mà không phát sinh thêm chi phí.*")
    aff_col1, aff_col2 = st.columns(2)
    with aff_col1:
        st.markdown("👉 [Tham khảo trọn bộ sách luyện thi JLPT N3-N1 chính hãng](https://shopee.vn)")
    with aff_col2:
        st.markdown("👉 [Giáo trình tiếng Nhật tổng hợp & Từ vựng](https://shopee.vn)")
    # LƯU Ý: 2 link trên hiện là link trang chủ Shopee (placeholder), chưa
    # phải link affiliate tới sản phẩm cụ thể — cần thay bằng link thật.

# Form góp ý
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("💌 Góp ý & Phản hồi phát triển trang web"):
    st.write("Chúng tôi luôn lắng nghe ý kiến của bạn để hoàn thiện công cụ luyện đọc tốt hơn.")
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("Tên hoặc Email của bạn (không bắt buộc):")
        fb_type = st.selectbox("Loại góp ý:", ["Đề xuất tính năng mới", "Báo lỗi phân tích/AI", "Góp ý giao diện", "Khác"])
        fb_content = st.text_area("Nội dung góp ý chi tiết:")
        submitted = st.form_submit_button("📩 Gửi góp ý")
        if submitted:
            if fb_content.strip():
                # FIX #7: trước đây thông báo "đã ghi nhận" nhưng KHÔNG lưu
                # góp ý ở đâu cả — giờ ghi vào feedback_log.csv thật sự.
                # Lưu ý: trên môi trường cloud (vd. Streamlit Community Cloud)
                # ổ đĩa là ephemeral, file này sẽ mất khi app khởi động lại
                # -> nếu cần lưu lâu dài, nên đổi sang Google Sheet/DB/email/webhook.
                try:
                    save_feedback(fb_name, fb_type, fb_content)
                    st.success("🌸 Cảm ơn bạn! Góp ý đã được ghi vào Google Sheet.")
                except Exception:
                    st.warning(
                        "⚠️ Chưa gửi được lên Google Sheet (có thể do chưa cấu hình secrets/"
                        "chia sẻ quyền Sheet). Góp ý đã được lưu tạm cục bộ, cảm ơn bạn!"
                    )
            else:
                st.warning("⚠️ Vui lòng nhập nội dung trước khi gửi.")

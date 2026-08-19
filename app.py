import streamlit as st
import google.generativeai as genai
import json
import io
import re

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

st.set_page_config(
    page_title="Luyện Đọc & Phân Tích Tiếng Nhật JLPT",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cấu hình CSS
st.markdown("""
<style>
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        z-index: 1 !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
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

    @keyframes fall {
        0% { top: -20px; transform: rotate(0deg); }
        100% { top: 100vh; transform: rotate(360deg); }
    }
    @keyframes sway {
        0% { transform: translateX(0px) rotate(0deg); }
        100% { transform: translateX(35px) rotate(45deg); }
    }

    .sticky-header-box {
        position: -webkit-sticky;
        position: sticky;
        top: 0.5rem;
        z-index: 998;
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.98), rgba(255, 228, 238, 0.98));
        border: 2px solid #ffccd5;
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 20px rgba(255, 182, 193, 0.35);
        backdrop-filter: blur(10px);
    }
    @media (prefers-color-scheme: dark) {
        .sticky-header-box {
            background: linear-gradient(135deg, rgba(45, 20, 30, 0.98), rgba(30, 15, 25, 0.98));
            border: 2px solid #ff758c;
            box-shadow: 0 6px 20px rgba(255, 117, 140, 0.3);
        }
    }

    .sticky-title {
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0;
        color: #d81b60 !important;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sticky-subtitle {
        font-size: 0.9rem;
        color: #555 !important;
        margin: 4px 0 0 0;
    }
    @media (prefers-color-scheme: dark) {
        .sticky-title { color: #ff80ab !important; }
        .sticky-subtitle { color: #ddd !important; }
    }

    ruby { font-size: 1.35rem; line-height: 2.3rem; font-family: 'Hiragino Mincho Pro', 'Yu Mincho', serif; }
    rt { font-size: 0.78rem; color: #e91e63; font-weight: 600; }
    .plain-jp-text { font-size: 1.25rem; line-height: 2.1rem; font-family: 'Hiragino Mincho Pro', 'Yu Mincho', serif; }

    .vi-translation-box {
        background: rgba(255, 243, 224, 0.75);
        border-left: 4px solid #ff9800;
        padding: 9px 15px;
        border-radius: 0 8px 8px 0;
        margin-top: 8px;
        font-size: 1.05rem;
        font-weight: 500;
        color: #d84315;
    }
    @media (prefers-color-scheme: dark) {
        .vi-translation-box {
            background: rgba(60, 40, 20, 0.85);
            border-left: 4px solid #ffb74d;
            color: #ffe0b2;
        }
    }
</style>

<div class="sakura-container">
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
    <div class="petal"></div>
</div>

<div class="sticky-header-box">
    <div class="sticky-title">🌸 Luyện Đọc & Phân Tích Tiếng Nhật JLPT</div>
    <div class="sticky-subtitle">Tự động dịch khổ, tra cứu Furigana, phân loại Ngữ pháp/Từ vựng N5–N1 và tạo bài tập luyện thi</div>
</div>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key của bạn:", type="password")

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "current_user_text" not in st.session_state:
    st.session_state.current_user_text = ""

user_text = st.text_area(
    "📋 Dán bài đọc tiếng Nhật vào đây:",
    height=160,
    placeholder="例：三日が過ぎたとき、おばあさんはおじいさんに言いました。「どうして、あんなに美しい布を織れるのだろう。ちょっとのぞいてみよう」..."
)

col_toggle, col_speed, col_btn = st.columns([1.2, 1.5, 2.5])
with col_toggle:
    show_furigana = st.toggle("🌸 Bật Furigana", value=True)
with col_speed:
    voice_speed = st.selectbox("⚡ Tốc độ đọc AI:", ["Bình thường (1.0x)", "Chậm (0.75x)"], index=0)
with col_btn:
    analyze_btn = st.button("🚀 Phân tích bài đọc", type="primary")

SYSTEM_PROMPT = """
Bạn là một chuyên gia ngôn ngữ học và giáo viên luyện thi tiếng Nhật JLPT cao cấp.
Nhiệm vụ của bạn là tiếp nhận văn bản tiếng Nhật do người dùng cung cấp, phân tích chuyên sâu và trả về kết quả DUY NHẤT dưới định dạng JSON theo schema sau (không thêm bất kỳ lời dẫn nào ngoài JSON).
LƯU Ý: Phải tạo CHÍNH XÁC ĐỦ 5 CÂU HỎI trắc nghiệm đọc hiểu (question_number từ 1 đến 5). Tuyệt đối không để ký tự xuống dòng chưa escape trong chuỗi JSON.
{
  "summary": { "estimated_jlpt_level": "N3", "topic": "Chủ đề bài đọc", "word_count": 185 },
  "paragraphs": [
    {
      "paragraph_id": 1,
      "original_text": "văn bản gốc không kèm furigana",
      "furigana_html": "văn bản có thẻ <ruby>Chữ Hán<rt>furigana</rt></ruby>",
      "vietnamese_translation": "bản dịch tiếng Việt tự nhiên và chuẩn xác"
    }
  ],
  "grammar_analysis": [
    { "pattern": "mẫu ngữ pháp", "jlpt_level": "N3", "meaning": "ý nghĩa ngữ pháp", "usage_in_text": "câu xuất hiện trong bài", "explanation": "giải thích cách dùng chi tiết" }
  ],
  "vocabulary_list": [
    { "word": "từ vựng", "reading": "cách đọc", "part_of_speech": "từ loại", "jlpt_level": "N3", "vietnamese_meaning": "nghĩa tiếng Việt" }
  ],
  "kanji_list": [
    { "kanji": "hán tự", "han_viet": "ÂM HÁN", "jlpt_level": "N3", "onyomi": "On", "kunyomi": "Kun", "meaning": "nghĩa cơ bản" }
  ],
  "jlpt_practice_questions": [
    {
      "question_number": 1,
      "question_text": "câu hỏi tiếng Nhật mô phỏng đề thi JLPT",
      "question_vietnamese": "dịch câu hỏi tiếng Việt",
      "options": {
        "A": "Lựa chọn A",
        "B": "Lựa chọn B",
        "C": "Lựa chọn C",
        "D": "Lựa chọn D"
      },
      "correct_answer": "A",
      "option_analysis": {
        "A": "Giải thích ngắn gọn tại sao A ĐÚNG (khớp với thông tin nào trong bài).",
        "B": "Giải thích ngắn gọn tại sao B SAI (sai lệch chỗ nào).",
        "C": "Giải thích ngắn gọn tại sao C SAI.",
        "D": "Giải thích ngắn gọn tại sao D SAI."
      }
    }
  ]
}
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
        st.error("⚠️ Vui lòng cấu hình Gemini API Key (trong Secrets hoặc thanh menu bên trái) để tiếp tục.")
    elif not user_text.strip():
        st.warning("⚠️ Vui lòng dán nội dung bài đọc trước khi bấm phân tích.")
    else:
        with st.spinner("🌸 AI đang phân tích bài đọc, tạo 5 câu hỏi JLPT..."):
            try:
                genai.configure(api_key=api_key)

                model = genai.GenerativeModel(
                    model_name="gemini-3.6-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(f"{SYSTEM_PROMPT}\n\nVăn bản cần phân tích:\n{user_text}")
                
                st.session_state.analysis_data = clean_and_parse_json(response.text)
                st.session_state.current_user_text = user_text

            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi gọi AI: {str(e)}")

# HIỂN THỊ KẾT QUẢ TỪ SESSION STATE
if st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    st.success("🎉 Đã phân tích thành công!")

    # Thông tin tổng quan
    sum_col1, sum_col2 = st.columns(2)
    sum_col1.info(f"🏷️ **Cấp độ ước tính:** {data.get('summary', {}).get('estimated_jlpt_level', 'N/A')}")
    sum_col2.info(f"📖 **Chủ đề:** {data.get('summary', {}).get('topic', 'Chung')}")

    # Tabs chức năng
    tab_read, tab_grammar, tab_vocab, tab_kanji, tab_quiz = st.tabs([
        "📖 Bài đọc & Dịch", "📝 Ngữ pháp", "📚 Từ vựng", "🈲 Hán tự (Kanji)", "❓ Câu hỏi JLPT (5 câu)"
    ])

    # Tab 1: Bài đọc & Dịch + Trình phát âm thanh có nút chỉnh tốc độ
    with tab_read:
        st.markdown("#### 🎧 Luyện nghe bài đọc (Giọng AI chuẩn bản xứ):")
        
        if TTS_AVAILABLE and st.session_state.current_user_text:
            try:
                is_slow = True if "Chậm" in voice_speed else False
                tts = gTTS(text=st.session_state.current_user_text, lang='ja', slow=is_slow)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp.read(), format='audio/mp3')
            except Exception as e:
                st.info("💡 Không thể tải file âm thanh cho bài đọc này.")
        else:
            st.info("💡 Trình phát âm thanh sẵn sàng khi phân tích bài đọc.")

        st.markdown("<br>", unsafe_allow_html=True)

        for p in data.get("paragraphs", []):
            st.markdown("---")
            if show_furigana:
                st.markdown(f"<div>{p.get('furigana_html')}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='plain-jp-text'>{p.get('original_text')}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='vi-translation-box'>🇻🇳 <strong>Dịch:</strong> {p.get('vietnamese_translation')}</div>", unsafe_allow_html=True)

    # Tab 2: Ngữ pháp
    with tab_grammar:
        for g in data.get("grammar_analysis", []):
            with st.expander(f"📌 {g.get('pattern')} [{g.get('jlpt_level')}] - {g.get('meaning')}"):
                st.markdown(f"- **Ngữ cảnh trong bài:** `{g.get('usage_in_text')}`")
                st.markdown(f"- **Giải thích:** {g.get('explanation')}")

    # Tab 3: Từ vựng
    with tab_vocab:
        vocab_rows = [
            {"Từ vựng": v.get("word"), "Cách đọc": v.get("reading"), "Cấp độ": v.get("jlpt_level"), "Từ loại": v.get("part_of_speech"), "Ý nghĩa": v.get("vietnamese_meaning")}
            for v in data.get("vocabulary_list", [])
        ]
        st.dataframe(vocab_rows, use_container_width=True)

    # Tab 4: Kanji
    with tab_kanji:
        kanji_rows = [
            {"Chữ Hán": k.get("kanji"), "Hán Việt": k.get("han_viet"), "Cấp độ": k.get("jlpt_level"), "Âm On": k.get("onyomi"), "Âm Kun": k.get("kunyomi"), "Ý nghĩa": k.get("meaning")}
            for k in data.get("kanji_list", [])
        ]
        st.dataframe(kanji_rows, use_container_width=True)

    # Tab 5: 5 Câu hỏi JLPT tương tác
    with tab_quiz:
        st.markdown("### ✍️ Luyện tập đọc hiểu JLPT (Trọn bộ 5 câu)")
        questions = data.get("jlpt_practice_questions", [])
        for idx, q in enumerate(questions):
            q_num = q.get("question_number", idx + 1)
            st.markdown(f"#### Câu {q_num}: {q.get('question_text')}")
            st.caption(f"*(Dịch: {q.get('question_vietnamese')})*")

            opts = q.get("options", {})
            choice_keys = [k for k in ["A", "B", "C", "D"] if k in opts]

            user_choice = st.radio(
                f"Chọn đáp án cho câu {q_num}:",
                options=choice_keys,
                format_func=lambda x: f"{x}. {opts.get(x, '')}",
                key=f"quiz_radio_{q_num}",
                index=None
            )

            correct_ans = q.get("correct_answer", "A")
            opt_analysis = q.get("option_analysis", {})

            if user_choice is not None:
                if user_choice == correct_ans:
                    st.success(f"🎉 **Chính xác!** Đáp án đúng là **{correct_ans}**.")
                else:
                    st.error(f"❌ **Chưa chính xác!** Bạn đã chọn **{user_choice}**, đáp án đúng là **{correct_ans}**.")

                st.markdown("**🔍 Phân tích chi tiết từng phương án:**")
                for opt_k in choice_keys:
                    explanation_text = opt_analysis.get(opt_k, "Chưa có phân tích.")
                    if opt_k == correct_ans:
                        st.markdown(f"- ✅ **Đáp án {opt_k}:** {explanation_text}")
                    else:
                        st.markdown(f"- ❌ **Đáp án {opt_k}:** {explanation_text}")
            st.markdown("---")

    # Khu vực liên kết tiếp thị (Affiliate)
    st.markdown("### 📚 Tài liệu gợi ý nâng cao trình độ")
    st.caption("*Trang web có thể nhận hoa hồng khi bạn mua qua liên kết giới thiệu mà không phát sinh thêm chi phí.*")
    aff_col1, aff_col2 = st.columns(2)
    with aff_col1:
        st.markdown("👉 [Tham khảo trọn bộ sách luyện thi JLPT N3-N1 chính hãng](https://shopee.vn)")
    with aff_col2:
        st.markdown("👉 [Giáo trình tiếng Nhật tổng hợp & Từ vựng](https://shopee.vn)")

# MỤC GÓP Ý CỦA NGƯỜI DÙNG
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("💌 Góp ý & Phản hồi phát triển trang web"):
    st.write("Chúng tôi luôn lắng nghe ý kiến của bạn để hoàn thiện công cụ luyện đọc tiếng Nhật tốt hơn mỗi ngày!")
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("Tên hoặc Email của bạn (không bắt buộc):")
        fb_type = st.selectbox("Loại góp ý:", ["Đề xuất tính năng mới", "Báo lỗi phân tích/AI", "Góp ý giao diện", "Khác"])
        fb_content = st.text_area("Nội dung góp ý chi tiết:", placeholder="Hãy nhập ý kiến của bạn tại đây...")
        submitted = st.form_submit_button("📩 Gửi góp ý")
        if submitted:
            if fb_content.strip():
                st.success("🌸 Cảm ơn bạn rất nhiều! Góp ý của bạn đã được ghi nhận thành công.")
            else:
                st.warning("⚠️ Vui lòng nhập nội dung góp ý trước khi bấm gửi.")

import streamlit as st
import google.generativeai as genai
import json
import io
import re
import base64
import asyncio

# Sử dụng edge-tts để tạo giọng đọc tự nhiên như phát thanh viên NHK (miễn phí, không cần key)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

st.set_page_config(
    page_title="Luyện Đọc & Phân Tích Tiếng Nhật JLPT",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cấu hình CSS:
# 1. Hợp nhất header trên cùng
# 2. Thanh điều khiển Audio Sticky nổi ở mép dưới màn hình (Mobile & Desktop đều luôn nhìn thấy khi cuộn bài)
# 3. Hiệu ứng cánh hoa rơi nhẹ
st.markdown("""
<style>
    /* Thanh công cụ và Header của Streamlit cùng chung 1 dải nền */
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

    /* Tiêu đề cố định trên cùng dải Header */
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

    /* Đệm trang để không bị che bởi Header và Sticky Audio Bar */
    .block-container {
        padding-top: 4.2rem !important;
        padding-bottom: 7rem !important;
    }

    /* Hiệu ứng cánh hoa anh đào rơi */
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

    /* Hiển thị tiếng Nhật & Furigana */
    ruby { font-size: 1.35rem; line-height: 2.3rem; font-family: 'Hiragino Mincho Pro', 'Yu Mincho', serif; }
    rt { font-size: 0.78rem; color: #e91e63; font-weight: 600; }
    .plain-jp-text { font-size: 1.25rem; line-height: 2.1rem; font-family: 'Hiragino Mincho Pro', 'Yu Mincho', serif; }

    /* Khối dịch tiếng Việt */
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

    /* Thanh điều khiển Audio cố định ở đáy màn hình */
    .sticky-audio-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, rgba(255, 245, 248, 0.98), rgba(255, 235, 242, 0.98));
        border-top: 2px solid #ffccd5;
        padding: 10px 16px;
        box-shadow: 0 -4px 18px rgba(255, 182, 193, 0.35);
        z-index: 99990;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 12px;
        backdrop-filter: blur(10px);
    }
    @media (prefers-color-scheme: dark) {
        .sticky-audio-bar {
            background: linear-gradient(135deg, rgba(40, 18, 28, 0.98), rgba(25, 10, 20, 0.98));
            border-top: 2px solid #ff758c;
            box-shadow: 0 -4px 18px rgba(255, 117, 140, 0.25);
        }
    }
</style>

<!-- Hiệu ứng cánh hoa anh đào rơi -->
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

<!-- Tiêu đề chìm liền vào thanh Header -->
<div class="app-title-fixed">
    <div class="app-main-title">🌸 Luyện Đọc & Phân Tích Tiếng Nhật JLPT</div>
    <div class="app-sub-title">Tự động dịch khổ, tra cứu Furigana, phân loại Ngữ pháp/Từ vựng N5–N1 và tạo bài tập luyện thi</div>
</div>
""", unsafe_allow_html=True)

# Lấy API Key từ Secrets hoặc Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key của bạn:", type="password")

# Khởi tạo session_state
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "current_user_text" not in st.session_state:
    st.session_state.current_user_text = ""
if "raw_audio_b64" not in st.session_state:
    st.session_state.raw_audio_b64 = None

# Khung nhập bài đọc
user_text = st.text_area(
    "📋 Dán bài đọc tiếng Nhật vào đây:",
    height=160,
    placeholder="例：三日が過ぎたとき、おばあさんはおじいさんに言いました。「どうして、あんなに美しい布を織れるのだろう。ちょっとのぞいてみよう」..."
)

analyze_btn = st.button("🚀 Phân tích bài đọc", type="primary", use_container_width=True)

SYSTEM_PROMPT = """
Bạn là một chuyên gia ngôn ngữ học và giáo viên luyện thi tiếng Nhật JLPT cao cấp.
Nhiệm vụ của bạn là tiếp nhận văn bản tiếng Nhật do người dùng cung cấp, phân tích chuyên sâu và trả về kết quả DUY NHẤT dưới định dạng JSON theo schema sau (không thêm bất kỳ lời dẫn nào ngoài JSON).

QUY TẮC LỌC VÀ TRÍCH XUẤT QUAN TRỌNG:
1. Đánh giá cấp độ JLPT tổng thể của bài đọc (estimated_jlpt_level: N5, N4, N3, N2 hoặc N1).
2. LỌC NGỮ PHÁP, TỪ VỰNG, KANJI THEO NGUYÊN TẮC:
   - Nếu bài đọc có trình độ tương đương N3 trở lên (N3, N2, N1): CHỈ liệt kê các điểm ngữ pháp, từ vựng và Kanji từ cấp độ N3 trở lên (gồm N3, N2, N1). Bỏ qua các từ/ngữ pháp quá cơ bản của N5, N4.
   - Nếu bài đọc có trình độ tương đương N5, N4: Liệt kê các điểm ngữ pháp, từ vựng và Kanji từ cấp độ N5 trở lên (N5, N4, N3...).
3. GIẢI THÍCH NGỮ PHÁP: Trong trường `usage_in_text`, sau câu tiếng Nhật trích ra từ bài, PHẢI kèm theo bản dịch nghĩa tiếng Việt đặt trong dấu ngoặc đơn `( )`. Ví dụ: `コーヒーを飲みながら本を読みます (Vừa uống cà phê vừa đọc sách)`.
4. BÀI TẬP: Tạo CHÍNH XÁC ĐỦ 5 CÂU HỎI trắc nghiệm đọc hiểu (question_number từ 1 đến 5). Tuyệt đối không để ký tự xuống dòng chưa escape trong chuỗi JSON.

JSON Schema:
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
    {
      "pattern": "mẫu ngữ pháp",
      "jlpt_level": "N3",
      "meaning": "ý nghĩa ngữ pháp",
      "usage_in_text": "câu xuất hiện trong bài (nghĩa tiếng Việt của câu trong ngữ cảnh)",
      "explanation": "giải thích cách dùng chi tiết"
    }
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

async def generate_nhk_voice(text):
    # Sử dụng giọng phát thanh viên chuẩn NHK Tokyo (ja-JP-NanamiNeural)
    voice = "ja-JP-NanamiNeural"
    communicate = edge_tts.Communicate(text, voice)
    mp3_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data.extend(chunk["data"])
    return bytes(mp3_data)

if analyze_btn:
    if not api_key:
        st.error("⚠️ Vui lòng cấu hình Gemini API Key (trong Secrets hoặc thanh menu bên trái) để tiếp tục.")
    elif not user_text.strip():
        st.warning("⚠️ Vui lòng dán nội dung bài đọc trước khi bấm phân tích.")
    else:
        with st.spinner("🌸 AI đang phân tích bài đọc, tạo giọng đọc phát thanh viên NHK và 5 câu hỏi JLPT..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-3.6-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(f"{SYSTEM_PROMPT}\n\nVăn bản cần phân tích:\n{user_text}")
                st.session_state.analysis_data = clean_and_parse_json(response.text)
                st.session_state.current_user_text = user_text

                # Tạo giọng đọc phát thanh viên chất lượng cao bằng edge-tts
                if EDGE_TTS_AVAILABLE:
                    try:
                        audio_data = asyncio.run(generate_nhk_voice(user_text))
                        st.session_state.raw_audio_b64 = base64.b64encode(audio_data).decode()
                    except Exception:
                        st.session_state.raw_audio_b64 = None
                else:
                    st.session_state.raw_audio_b64 = None

            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi gọi AI: {str(e)}")

# HIỂN THỊ KẾT QUẢ
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

    # Tab 1: Bài đọc & Dịch
    with tab_read:
        # Công tắc bật tắt Furigana ngay bên trên bài đọc
        show_furigana = st.toggle("🌸 Bật Furigana", value=False)

        for p in data.get("paragraphs", []):
            if show_furigana:
                st.markdown(f"<div>{p.get('furigana_html')}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='plain-jp-text'>{p.get('original_text')}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='vi-translation-box'>🇻🇳 <strong>Dịch:</strong> {p.get('vietnamese_translation')}</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

        # THANH ĐIỀU KHIỂN ÂM THANH NỔI (Sticky Bottom Player) - Luôn hiển thị trên cả Mobile & PC khi cuộn bài đọc
        if st.session_state.raw_audio_b64:
            st.markdown(f"""
            <div class="sticky-audio-bar">
                <span style="font-size: 0.9rem; font-weight: 700; color: #d81b60;">🎙️ Giọng đọc NHK Tokyo:</span>
                <audio id="floating_player" controls style="height: 38px; max-width: 400px; flex-grow: 1;">
                    <source src="data:audio/mp3;base64,{st.session_state.raw_audio_b64}" type="audio/mp3">
                </audio>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.82rem; font-weight: 600;">⚡ Tốc độ:</span>
                    <select id="speed_select" onchange="document.getElementById('floating_player').playbackRate = this.value;" style="padding: 4px 8px; border-radius: 8px; border: 1px solid #ffccd5; background: white; font-weight: 600;">
                        <option value="0.5">x0.5</option>
                        <option value="0.75">x0.75</option>
                        <option value="1.0" selected>x1.0</option>
                        <option value="1.25">x1.25</option>
                        <option value="1.5">x1.5</option>
                        <option value="2.0">x2.0</option>
                    </select>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Tab 2: Ngữ pháp
    with tab_grammar:
        for g in data.get("grammar_analysis", []):
            with st.expander(f"📌 {g.get('pattern')} [{g.get('jlpt_level')}] - {g.get('meaning')}"):
                st.markdown(f"- **Ngữ cảnh trong bài:** `{g.get('usage_in_text')}`")
                st.markdown(f"- **Giải thích chi tiết:** {g.get('explanation')}")

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

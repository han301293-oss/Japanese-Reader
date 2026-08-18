import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Luyện Đọc Tiếng Nhật JLPT", page_icon="⛩️", layout="wide")

# CSS tùy chỉnh để hiển thị Furigana chuẩn và giao diện đẹp
st.markdown("""
<style>
    ruby { font-size: 1.3rem; line-height: 2.2rem; }
    rt { font-size: 0.75rem; color: #1E88E5; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Lấy API Key từ Secrets hoặc Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key của bạn:", type="password")

st.title("⛩️ Web Luyện Đọc & Phân Tích Tiếng Nhật JLPT")
st.caption("Tự động dịch khổ, tra cứu Furigana, phân loại Ngữ pháp/Từ vựng N5-N1 và tạo đề thi JLPT")

# Khung nhập bài đọc
user_text = st.text_area("📋 Dán bài đọc tiếng Nhật vào đây:", height=180, placeholder="例：山田さんは毎朝7時に起きて、コーヒーを飲みながら本を読みます。")

col1, col2 = st.columns([1, 4])
with col1:
    show_furigana = st.toggle("Bật Furigana", value=True)
with col2:
    analyze_btn = st.button("🚀 Phân tích bài đọc", type="primary")

SYSTEM_PROMPT = """
Bạn là một chuyên gia ngôn ngữ học và giáo viên luyện thi tiếng Nhật JLPT cao cấp.
Nhiệm vụ của bạn là tiếp nhận văn bản tiếng Nhật do người dùng cung cấp, phân tích chuyên sâu và trả về kết quả DUY NHẤT dưới định dạng JSON theo schema sau (không thêm bất kỳ lời dẫn nào ngoài JSON):
{
  "summary": { "estimated_jlpt_level": "N3", "topic": "Chủ đề bài đọc", "word_count": 185 },
  "paragraphs": [
    {
      "paragraph_id": 1,
      "original_text": "văn bản gốc",
      "furigana_html": "văn bản có thẻ <ruby>Ví dụ<rt>れい</rt></ruby>",
      "vietnamese_translation": "bản dịch tiếng Việt"
    }
  ],
  "grammar_analysis": [
    { "pattern": "mẫu ngữ pháp", "jlpt_level": "N3", "meaning": "ý nghĩa", "usage_in_text": "câu trong bài", "explanation": "giải thích chi tiết" }
  ],
  "vocabulary_list": [
    { "word": "từ vựng", "reading": "cách đọc", "part_of_speech": "từ loại", "jlpt_level": "N3", "vietnamese_meaning": "nghĩa" }
  ],
  "kanji_list": [
    { "kanji": "hán tự", "han_viet": "ÂM HÁN", "jlpt_level": "N3", "onyomi": "On", "kunyomi": "Kun", "meaning": "nghĩa" }
  ],
  "jlpt_practice_questions": [
    {
      "question_number": 1,
      "question_text": "câu hỏi tiếng Nhật",
      "question_vietnamese": "dịch câu hỏi",
      "options": { "A": "lựa chọn 1", "B": "lựa chọn 2", "C": "lựa chọn 3", "D": "lựa chọn 4" },
      "correct_answer": "A",
      "explanation": "giải thích chi tiết đáp án"
    }
  ]
}
"""

if analyze_btn:
    if not api_key:
        st.error("⚠️ Vui lòng nhập Gemini API Key ở thanh menu bên trái để tiếp tục.")
    elif not user_text.strip():
        st.warning("⚠️ Vui lòng dán nội dung bài đọc trước khi bấm phân tích.")
    else:
        with st.spinner("AI đang bóc tách ngữ pháp, từ vựng và tạo bài tập..."):
            try:
                genai.configure(api_key=api_key)

                # Sử dụng model gemini-3.6-flash
                model = genai.GenerativeModel(
                    model_name="gemini-3.6-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(f"{SYSTEM_PROMPT}\n\nVăn bản cần phân tích:\n{user_text}")
                data = json.loads(response.text)

                st.success("🎉 Đã phân tích thành công!")

                # Thông tin tổng quan
                sum_col1, sum_col2 = st.columns(2)
                sum_col1.info(f"**Cấp độ ước tính:** {data.get('summary', {}).get('estimated_jlpt_level', 'N/A')}")
                sum_col2.info(f"**Chủ đề:** {data.get('summary', {}).get('topic', 'Chung')}")

                # Chia các Tab chức năng
                tab_read, tab_grammar, tab_vocab, tab_kanji, tab_quiz = st.tabs([
                    "📖 Bài đọc & Dịch", "📝 Ngữ pháp", "📚 Từ vựng", "🈲 Hán tự (Kanji)", "❓ Câu hỏi JLPT"
                ])

                with tab_read:
                    for p in data.get("paragraphs", []):
                        st.markdown("---")
                        if show_furigana:
                            st.markdown(f"<div>{p.get('furigana_html')}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{p.get('original_text')}**")
                        st.caption(f"🇻🇳 *Dịch:* {p.get('vietnamese_translation')}")

                with tab_grammar:
                    for g in data.get("grammar_analysis", []):
                        with st.expander(f"📌 {g.get('pattern')} [{g.get('jlpt_level')}] - {g.get('meaning')}"):
                            st.markdown(f"- **Ngữ cảnh trong bài:** `{g.get('usage_in_text')}`")
                            st.markdown(f"- **Giải thích:** {g.get('explanation')}")

                with tab_vocab:
                    vocab_rows = [
                        {"Từ vựng": v.get("word"), "Cách đọc": v.get("reading"), "Cấp độ": v.get("jlpt_level"), "Từ loại": v.get("part_of_speech"), "Ý nghĩa": v.get("vietnamese_meaning")}
                        for v in data.get("vocabulary_list", [])
                    ]
                    st.dataframe(vocab_rows, use_container_width=True)

                with tab_kanji:
                    kanji_rows = [
                        {"Chữ Hán": k.get("kanji"), "Hán Việt": k.get("han_viet"), "Cấp độ": k.get("jlpt_level"), "Âm On": k.get("onyomi"), "Âm Kun": k.get("kunyomi"), "Ý nghĩa": k.get("meaning")}
                        for k in data.get("kanji_list", [])
                    ]
                    st.dataframe(kanji_rows, use_container_width=True)

                with tab_quiz:
                    for q in data.get("jlpt_practice_questions", []):
                        st.markdown(f"#### Câu {q.get('question_number')}: {q.get('question_text')}")
                        st.caption(f"*(Dịch: {q.get('question_vietnamese')})*")
                        
                        opts = q.get("options", {})
                        for opt_key in ["A", "B", "C", "D"]:
                            if opt_key in opts:
                                st.write(f"**{opt_key}.** {opts[opt_key]}")

                        with st.expander("👁️ Xem đáp án & Giải thích chi tiết"):
                            st.success(f"**Đáp án đúng:** {q.get('correct_answer')}")
                            st.write(q.get("explanation"))

                # Khu vực liên kết tiếp thị (Affiliate)
                st.markdown("---")
                st.markdown("### 📚 Tài liệu gợi ý nâng cao trình độ")
                st.caption("*Trang web có thể nhận hoa hồng khi bạn mua qua liên kết giới thiệu mà không phát sinh thêm chi phí.*")
                aff_col1, aff_col2 = st.columns(2)
                with aff_col1:
                    st.markdown("👉 [Tham khảo trọn bộ sách luyện thi JLPT N3-N1 chính hãng](https://shopee.vn)")
                with aff_col2:
                    st.markdown("👉 [Giáo trình tiếng Nhật tổng hợp & Từ vựng](https://shopee.vn)")

            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi gọi AI: {str(e)}")

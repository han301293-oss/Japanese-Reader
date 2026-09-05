if st.session_state.raw_audio_b64:
            st.markdown(
                f"""
            <div class="sticky-audio-bar">
                <span style="font-size: 0.9rem; font-weight: 700; color: #d81b60;">🎙️ Giọng đọc chuẩn Tokyo (NHK):</span>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <button onclick="let p = document.getElementById('floating_player'); if(p) p.currentTime = Math.max(0, p.currentTime - 10);" 
                            style="padding: 4px 10px; border-radius: 8px; border: 1px solid #ffccd5; background: white; font-weight: 700; font-size: 0.82rem; cursor: pointer; color: #d81b60;">
                        ⏮️ -10s
                    </button>
                    <button onclick="let p = document.getElementById('floating_player'); if(p) p.currentTime = Math.min(p.duration || 0, p.currentTime + 10);" 
                            style="padding: 4px 10px; border-radius: 8px; border: 1px solid #ffccd5; background: white; font-weight: 700; font-size: 0.82rem; cursor: pointer; color: #d81b60;">
                        +10s ⏭️
                    </button>
                </div>
                <audio id="floating_player" controls style="height: 38px; max-width: 360px; flex-grow: 1;">
                    <source src="data:audio/mp3;base64,{st.session_state.raw_audio_b64}" type="audio/mp3">
                </audio>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 0.82rem; font-weight: 600;">⚡ Tốc độ:</span>
                    <select id="speed_select" onchange="document.getElementById('floating_player').playbackRate = this.value;" style="padding: 4px 8px; border-radius: 8px; border: 1px solid #ffccd5; background: white; font-weight: 600; cursor: pointer;">
                        <option value="0.5">x0.5 (Rất chậm)</option>
                        <option value="0.75">x0.75 (Chậm)</option>
                        <option value="1.0" selected>x1.0 (Chuẩn)</option>
                        <option value="1.25">x1.25 (Nhanh vừa)</option>
                        <option value="1.5">x1.5 (Nhanh)</option>
                        <option value="1.75">x1.75 (Rất nhanh)</option>
                        <option value="2.0">x2.0 (Cực nhanh)</option>
                    </select>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

if st.session_state.raw_audio_b64:
            st.markdown(
                f"""
            <div class="sticky-audio-bar">
                <span style="font-size: 0.9rem; font-weight: 700; color: #d81b60;">🎙️ Tokyo NHK:</span>
                
                <audio id="floating_player">
                    <source src="data:audio/mp3;base64,{st.session_state.raw_audio_b64}" type="audio/mp3">
                </audio>

                <!-- Cụm nút: Tua lại 10s - Nút Play/Pause tam giác - Tua đi 10s -->
                <div style="display: flex; align-items: center; gap: 8px;">
                    <!-- Mũi tên cong tua lại 10s -->
                    <button onclick="let p = document.getElementById('floating_player'); if(p) p.currentTime = Math.max(0, p.currentTime - 10);" 
                            title="Tua lại 10 giây"
                            style="background: white; border: 1.5px solid #ffccd5; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #d81b60; padding: 0;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M1 4v6h6"></path>
                            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                            <text x="12" y="15" font-size="7.5" font-weight="900" fill="#d81b60" stroke="none" text-anchor="middle" font-family="sans-serif">10</text>
                        </svg>
                    </button>

                    <!-- Nút Play tam giác / Pause -->
                    <button id="play_btn" 
                            onclick="let p = document.getElementById('floating_player'); let icon = document.getElementById('play_icon'); if(p.paused){{ p.play(); icon.innerHTML = '&#10074;&#10074;'; }}else{{ p.pause(); icon.innerHTML = '&#9658;'; }}"
                            title="Phát / Dừng"
                            style="background: #d81b60; border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; box-shadow: 0 2px 8px rgba(216,27,96,0.3); padding: 0;">
                        <span id="play_icon" style="font-size: 1.15rem; margin-left: 2px;">&#9658;</span>
                    </button>

                    <!-- Mũi tên cong tua đi 10s -->
                    <button onclick="let p = document.getElementById('floating_player'); if(p) p.currentTime = Math.min(p.duration || 0, p.currentTime + 10);" 
                            title="Tua tiếp 10 giây"
                            style="background: white; border: 1.5px solid #ffccd5; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #d81b60; padding: 0;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M23 4v6h-6"></path>
                            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                            <text x="12" y="15" font-size="7.5" font-weight="900" fill="#d81b60" stroke="none" text-anchor="middle" font-family="sans-serif">10</text>
                        </svg>
                    </button>
                </div>

                <!-- Tùy chỉnh tốc độ -->
                <div style="display: flex; align-items: center; gap: 4px;">
                    <select id="speed_select" onchange="document.getElementById('floating_player').playbackRate = this.value;" 
                            style="padding: 4px 8px; border-radius: 8px; border: 1px solid #ffccd5; background: white; font-weight: 700; font-size: 0.82rem; cursor: pointer; color: #d81b60;">
                        <option value="0.5">x0.5</option>
                        <option value="0.75">x0.75</option>
                        <option value="1.0" selected>x1.0</option>
                        <option value="1.25">x1.25</option>
                        <option value="1.5">x1.5</option>
                        <option value="1.75">x1.75</option>
                        <option value="2.0">x2.0</option>
                    </select>
                </div>
            </div>

            <script>
                // Tự động chuyển icon về tam giác khi phát hết bài
                let aud = document.getElementById('floating_player');
                if (aud) {{
                    aud.onended = function() {{
                        let icon = document.getElementById('play_icon');
                        if (icon) icon.innerHTML = '&#9658;';
                    }};
                }}
            </script>
            """,
                unsafe_allow_html=True,
            )

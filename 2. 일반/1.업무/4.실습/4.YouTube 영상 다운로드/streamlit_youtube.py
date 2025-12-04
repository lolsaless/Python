# https://youtu.be/cAL-Z_FfObI?si=M7s2zO1Zuv8anKUw


import streamlit as st
import pandas as pd
import yt_dlp
import os
import subprocess
import re

# 제목 표시
st.title("🎞️ YouTube Downloader with Format Selector")

# 유튜브 링크 입력
url = st.text_input("YouTube 링크를 입력하세요:", "")

# ANSI 코드 제거용
ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

# 파일 이름에 사용할 수 없는 문자를 안전하게 제거
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

# 다운로드 진행 상황 표시용 hook
def make_hook(kind, progress_bar, status_text):
    def hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            percent_clean = ansi_escape.sub('', percent)  # ANSI 제거
            try:
                percent_num = float(percent_clean.strip('%')) / 100
                progress_bar.progress(percent_num)
                status_text.text(f"{kind} 다운로드 중: {percent_clean}")
            except:
                pass
        elif d['status'] == 'finished':
            progress_bar.progress(1.0)
            status_text.text(f"{kind} 다운로드 완료!")
    return hook

if url:
    with st.spinner("포맷 정보를 불러오는 중입니다..."):
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])

            # 유튜브 제목 → 병합 파일명에 사용
            video_title = info.get('title', 'final_output')
            safe_title = sanitize_filename(video_title)

            # 포맷 데이터프레임 생성
            format_data = []
            for f in formats:
                format_data.append({
                    'Format ID': f['format_id'],
                    'Resolution': str(f.get('height', 'audio only')),
                    'Filesize': str(f.get('filesize', 'unknown')),
                    'Note': f.get('format_note', 'unknown'),
                    'Type': 'audio' if f.get('vcodec', 'none') == 'none' else 'video',
                    'Extension': f.get('ext', 'unknown')
                })
            df = pd.DataFrame(format_data)

            st.success("포맷 목록 불러오기 완료!")
            st.dataframe(df)

            # 비디오/오디오 포맷 선택
            video_format = st.selectbox("🎬 비디오 포맷 선택 (ID):", df[df["Type"] == "video"]["Format ID"].tolist())
            selected_video_ext = df[df['Format ID'] == video_format]['Extension'].values[0]
            filtered_audio_df = df[(df["Type"] == "audio") & (df["Extension"] == selected_video_ext)]

            if filtered_audio_df.empty:
                st.warning(f"⚠️ '{selected_video_ext}' 확장자에 맞는 오디오 포맷이 없습니다.")
                audio_format = None
            else:
                audio_format = st.selectbox(f"🎧 오디오 포맷 선택 (ID, 확장자: {selected_video_ext}):", filtered_audio_df["Format ID"].tolist())

            if st.button("📥 다운로드 및 병합"):
                if not audio_format:
                    st.error("❌ 오디오 포맷이 선택되지 않았습니다.")
                else:
                    video_output = f"video_only.{selected_video_ext}"
                    audio_output = f"audio_only.{selected_video_ext}"
                    merged_output = f"{safe_title}.mp4"

                    try:
                        # 비디오 다운로드
                        st.subheader("📤 다운로드 진행 상황")
                        st.markdown("**비디오:**")
                        video_progress = st.progress(0)
                        video_status = st.empty()
                        ydl_opts_video = {
                            'format': video_format,
                            'outtmpl': video_output,
                            'ratelimit': 500000,
                            'progress_hooks': [make_hook("비디오", video_progress, video_status)],
                            'quiet': True
                        }
                        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                            ydl.download([url])

                        # 오디오 다운로드
                        st.markdown("**오디오:**")
                        audio_progress = st.progress(0)
                        audio_status = st.empty()
                        ydl_opts_audio = {
                            'format': audio_format,
                            'outtmpl': audio_output,
                            'ratelimit': 500000,
                            'progress_hooks': [make_hook("오디오", audio_progress, audio_status)],
                            'quiet': True
                        }
                        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                            ydl.download([url])

                        # 병합 실행
                        st.subheader("🎞️ 병합 중...")
                        merge_cmd = [
                            "ffmpeg", "-y",
                            "-i", video_output,
                            "-i", audio_output,
                            "-c:v", "copy",
                            "-c:a", "aac",
                            "-strict", "experimental",
                            merged_output
                        ]
                        result = subprocess.run(
                            merge_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            encoding='utf-8'  # 💡 인코딩 명시
                            )


                        if result.returncode == 0 and os.path.exists(merged_output):
                            st.success(f"✅ 병합 완료: {merged_output}")

                            # 💡 임시파일 삭제
                            if os.path.exists(video_output):
                                os.remove(video_output)
                            if os.path.exists(audio_output):
                                os.remove(audio_output)

                            # 다운로드 버튼
                            with open(merged_output, "rb") as file:
                                st.download_button(label="📦 다운로드: 병합된 영상", data=file, file_name=merged_output)
                        else:
                            st.error("❌ 병합 실패")
                            st.code(result.stderr)

                    except Exception as e:
                        st.error(f"오류 발생: {e}")

        except Exception as e:
            st.error(f"❗ 포맷 정보를 불러오는 중 오류 발생: {e}")
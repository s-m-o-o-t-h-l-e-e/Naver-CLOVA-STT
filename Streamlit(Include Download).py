import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import json
import tempfile
import os
import time

# CLOVA_API_URL = "your_API_url"
# CLOVA_SECRET_KEY = "your_secret_key"

st.set_page_config(page_title="Naver CLOVA STT Research", layout="wide")

def format_time_srt(ms):
    td = time.gmtime(ms / 1000)
    milli = int(ms % 1000)
    return f"{time.strftime('%H:%M:%S', td)},{milli:03d}"

def format_time_vtt(ms):
    td = time.gmtime(ms / 1000)
    milli = int(ms % 1000)
    return f"{time.strftime('%H:%M:%S', td)}.{milli:03d}"

def call_clova_stt(audio_path):
    headers = {"X-CLOVASPEECH-API-KEY": CLOVA_SECRET_KEY}
    request_body = {
        "language": "ko-KR",
        "completion": "sync",
        "fullText": True
    }
    
    with open(audio_path, 'rb') as f:
        files = {
            'media': f,
            'params': (None, json.dumps(request_body), 'application/json')
        }
        response = requests.post(CLOVA_API_URL, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Clova API 오류: {response.status_code} - {response.text}")

def main():
    st.title("🎵 Naver Clova 기반 음성 연구 대시보드")
    st.info("Clova STT를 사용하여 고정밀 텍스트 추출과 음향 분석을 수행합니다.")

    uploaded_file = st.file_uploader("분석할 오디오 파일(mp3, wav)을 선택하세요", type=["mp3", "wav"])

    if uploaded_file is not None:
        raw_filename = uploaded_file.name
        base_filename = os.path.splitext(raw_filename)[0]
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            status_text.text("1/3: Naver Clova로 텍스트 추출 중...")
            progress_bar.progress(30)
            
            res = call_clova_stt(tmp_path)
            extracted_text = res.get("text", "")
            segments = res.get("segments", []) 
            
            st.subheader("📝 Clova 텍스트 추출 결과")
            st.success(extracted_text if extracted_text else "추출된 텍스트가 없습니다.")
            st.divider()

            status_text.text("2/3: 음향 데이터 분석 중...")
            progress_bar.progress(60)
            y, sr = librosa.load(tmp_path)
            duration = librosa.get_duration(y=y, sr=sr)
            f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            avg_pitch = np.nanmean(f0) if np.any(~np.isnan(f0)) else 0
            word_count = len(extracted_text.split())
            speech_rate = word_count / (duration / 60) if duration > 0 else 0

            srt_lines, vtt_lines = [], ["WEBVTT\n"]
            for i, seg in enumerate(segments):
                start, end, text = seg['start'], seg['end'], seg['text']
                srt_lines.append(f"{i+1}\n{format_time_srt(start)} --> {format_time_srt(end)}\n{text}\n")
                vtt_lines.append(f"{format_time_vtt(start)} --> {format_time_vtt(end)}\n{text}\n")

            srt_final = "\n".join(srt_lines)
            vtt_final = "\n".join(vtt_lines)

            st.subheader("💾 분석 데이터 내보내기")
            
            tsv_df = pd.DataFrame([{"start": s['start'], "end": s['end'], "text": s['text']} for s in segments])
            tsv_data = tsv_df.to_csv(index=False, sep='\t').encode('utf-8-sig')

            dl_container = st.container(border=True)
            with dl_container:
                r1_c1, r1_c2, r1_c3 = st.columns(3)
                r1_c1.download_button("TXT 다운로드", extracted_text, f"{base_filename}_stt.txt", use_container_width=True)
                r1_c2.download_button("JSON(원본) 다운로드", json.dumps(res, indent=4, ensure_ascii=False), f"{base_filename}_raw.json", use_container_width=True)
                r1_c3.download_button("TSV 다운로드", tsv_data, f"{base_filename}_segments.tsv", use_container_width=True)
                
                r2_c1, r2_c2, r2_c3 = st.columns(3)
                r2_c1.download_button("SRT 자막 다운로드", srt_final, f"{base_filename}.srt", use_container_width=True)
                r2_c2.download_button("VTT 자막 다운로드", vtt_final, f"{base_filename}.vtt", use_container_width=True)
                
                report_df = pd.DataFrame({
                    "항목": ["평균 피치(Hz)", "총 시간(초)", "발화 속도(WPM)", "어절 수"],
                    "결과": [f"{avg_pitch:.2f}", f"{duration:.2f}", f"{speech_rate:.1f}", word_count]
                })
                r2_c3.download_button("보고서(CSV) 다운로드", report_df.to_csv(index=False).encode('utf-8-sig'), f"{base_filename}_report.csv", use_container_width=True)

            status_text.text(f"'{raw_filename}' 분석 완료!")
            progress_bar.progress(100)

        except Exception as e:
            st.error(f"오류 발생: {e}")        
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        st.warning("파일을 업로드해주세요.")

if __name__ == "__main__":

    main()



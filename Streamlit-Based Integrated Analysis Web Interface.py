import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import tempfile
import os
import time

# CLOVA_API_URL = "https://clovaspeech-gw.ncloud.com/external/v1/14442/d2150efca70e10fa8b827cf78830d813bed99a299604052e6448f8912170436b/recognizer/upload"
# CLOVA_SECRET_KEY = "ac9d86fd540d41e29b59d0ab591ffc02"

st.set_page_config(page_title="Naver CLOVA STT", layout="wide")

def call_clova_stt(audio_path):
    headers = {
        "X-CLOVASPEECH-API-KEY": CLOVA_SECRET_KEY
    }
    
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
        progress_bar = st.progress(0)
        status_text = st.empty()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            status_text.text("1/3: Naver Clova로 텍스트 추출 중...")
            progress_bar.progress(30)
            
            stt_start = time.time()
            res = call_clova_stt(tmp_path)
            stt_end = time.time()
            
            extracted_text = res.get("text", "추출된 텍스트가 없습니다.")
            
            st.subheader("📝 Clova 텍스트 추출 결과")
            st.write(f"⏱️ API 응답 시간: {stt_end - stt_start:.2f}초")
            st.success(extracted_text)
            st.divider()

            status_text.text("2/3: 음향 데이터 분석 중...")
            progress_bar.progress(60)
            
            y, sr = librosa.load(tmp_path)
            duration = librosa.get_duration(y=y, sr=sr)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📊 파형 및 피치 분석")
                fig, ax = plt.subplots(2, 1, figsize=(10, 8))
                librosa.display.waveshow(y, sr=sr, ax=ax[0])
                ax[0].set_title("Waveform")

                f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                ax[1].plot(f0, color='red')
                ax[1].set_title("Pitch Tracking (Hz)")
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.subheader("📈 연구 지표 요약")
                avg_pitch = np.nanmean(f0) if np.any(~np.isnan(f0)) else 0
                word_count = len(extracted_text.split())
                speech_rate = word_count / (duration / 60)

                m1, m2 = st.columns(2)
                m1.metric("평균 피치", f"{avg_pitch:.2f} Hz")
                m2.metric("총 시간", f"{duration:.2f} 초")
                
                m3, m4 = st.columns(2)
                m3.metric("발화 속도 (WPM)", f"{speech_rate:.1f}")
                m4.metric("추출 어절 수", f"{word_count} 개")

            status_text.text("분석 완료!")
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

# [실행 방법 안내]
# 일반적인 'python 파일명.py'로 실행하면 ScriptRunContext 오류가 발생합니다.
# 반드시 터미널에서 아래 명령어로 실행해야 정상적인 웹 인터페이스가 출력됩니다.
# ex）> streamlit run "Streamlit-Based Integrated Analysis Web Interface.py"


import numpy as np
import pyworld as pw
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import requests
import json
import warnings
import os

warnings.filterwarnings('ignore')

CLOVA_INVOKE_URL = 'https://clovaspeech-gw.ncloud.com/external/v1/14442/d2150efca70e10fa8b827cf78830d813bed99a299604052e6448f8912170436b'
CLOVA_SECRET_KEY = 'ac9d86fd540d41e29b59d0ab591ffc02'
AUDIO_FILE_PATH = r"C:\Users\coded\Desktop\sample\test_Korean_audio.mp3"
OUTPUT_VIDEO_PATH = "speech_analysis_result.mp4"

class NaverClovaSTT:
    def __init__(self, invoke_url, secret_key):
        self.invoke_url = invoke_url
        self.secret_key = secret_key

    def request_stt_analysis(self, file_path):
        request_config = {
            'language': 'ko-KR', 
            'completion': 'sync', 
            'diarization': {'enable' : True, 'speakerCount': 0}
        }
        headers = {
            'Accept': 'application/json', 
            'X-CLOVASPEECH-API-KEY': self.secret_key
        }
        with open(file_path, 'rb') as audio_file:
            files = {
                'media': audio_file, 
                'params': (None, json.dumps(request_config).encode('UTF-8'), 'application/json')
            }
            response = requests.post(f'{self.invoke_url}/recognizer/upload', headers=headers, files=files)
            return response.json()

if __name__ == '__main__':
    stt_client = NaverClovaSTT(CLOVA_INVOKE_URL, CLOVA_SECRET_KEY)
    stt_result = stt_client.request_stt_analysis(AUDIO_FILE_PATH)
    
    if 'text' not in stt_result:
        print("API 호출 실패:", stt_result)
        exit()
    
    utterance_segments = stt_result.get('segments', [])

    audio_signal, sample_rate = sf.read(AUDIO_FILE_PATH)
    if len(audio_signal.shape) > 1: 
        audio_signal = np.mean(audio_signal, axis=1)
    
    raw_pitch, pitch_timestamps = pw.dio(audio_signal.astype(np.float64), sample_rate)
    refined_pitch = pw.stonemask(audio_signal.astype(np.float64), raw_pitch, pitch_timestamps, sample_rate)
    speech_rate_values = np.zeros_like(pitch_timestamps)

    for segment in utterance_segments:
        start_time_sec = segment['start'] / 1000.0
        end_time_sec = segment['end'] / 1000.0
        text_content = segment['text'].replace(" ", "") 
        
        duration = end_time_sec - start_time_sec
        chars_per_second = len(text_content) / duration if duration > 0 else 0
        segment['calculated_rate'] = chars_per_second

        time_mask = (pitch_timestamps >= start_time_sec) & (pitch_timestamps <= end_time_sec)
        if np.any(time_mask):
            visual_jitter = np.random.normal(0, 0.2, size=np.sum(time_mask)) 
            speech_rate_values[time_mask] = chars_per_second + visual_jitter

    TIME_WINDOW_WIDTH = 10.0
    FPS = 30
    TOTAL_DURATION = len(audio_signal) / sample_rate
    TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

    fig, (ax_wave, ax_pitch, ax_rate) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 2, 2]})
    fig.patch.set_facecolor('black')

    line_waveform, = ax_wave.plot([], [], color='#1DB954', lw=1)
    ax_wave.set_facecolor('black')
    ax_wave.set_ylim(-1, 1)
    ax_wave.set_xlim(-TIME_WINDOW_WIDTH, 0)
    ax_wave.axis('off')

    line_pitch_graph, = ax_pitch.plot([], [], color='#FFD700', lw=2)
    ax_pitch.set_facecolor('black')
    ax_pitch.set_ylim(50, 450)
    ax_pitch.set_xlim(-TIME_WINDOW_WIDTH, 0)
    ax_pitch.set_ylabel("Pitch (Hz)", color='white')
    ax_pitch.grid(True, axis='y', color='#333333')
    ax_pitch.tick_params(colors='white')

    line_rate_graph, = ax_rate.plot([], [], color='#00BFFF', lw=1.5, alpha=0.8)
    ax_rate.set_facecolor('black')
    ax_rate.set_ylim(0, 15)
    ax_rate.set_xlim(-TIME_WINDOW_WIDTH, 0)
    ax_rate.set_ylabel("Speech Rate (CPS)", color='white')
    ax_rate.grid(True, axis='y', color='#333333')
    ax_rate.tick_params(colors='white')

    ui_speaker_label = ax_wave.text(0.02, 0.8, '', color='#1DB954', fontsize=12, fontweight='bold', transform=ax_wave.transAxes)
    ui_pitch_label = ax_pitch.text(0.02, 0.9, '', color='#FFD700', fontsize=12, fontweight='bold', transform=ax_pitch.transAxes)
    ui_rate_label = ax_rate.text(0.02, 0.9, '', color='#00BFFF', fontsize=12, fontweight='bold', transform=ax_rate.transAxes)

    def update_frame(frame_idx):
        current_time_sec = frame_idx / FPS
        window_start_time = max(0, current_time_sec - TIME_WINDOW_WIDTH)

        wave_start_idx = int(window_start_time * sample_rate)
        wave_end_idx = int(current_time_sec * sample_rate)
        wave_view_data = audio_signal[wave_start_idx:wave_end_idx:100]
        
        if len(wave_view_data) > 0:
            x_data = np.linspace(max(-current_time_sec, -TIME_WINDOW_WIDTH), 0, len(wave_view_data))
            line_waveform.set_data(x_data, wave_view_data)

        view_mask = (pitch_timestamps >= window_start_time) & (pitch_timestamps <= current_time_sec)

        visible_pitch = refined_pitch[view_mask].copy()
        visible_pitch[visible_pitch < 30] = np.nan
        line_pitch_graph.set_data(pitch_timestamps[view_mask] - current_time_sec, visible_pitch)

        visible_rates = speech_rate_values[view_mask].copy()
        visible_rates[visible_rates == 0] = np.nan
        line_rate_graph.set_data(pitch_timestamps[view_mask] - current_time_sec, visible_rates)

        current_idx = np.searchsorted(pitch_timestamps, current_time_sec)
        live_pitch_val = refined_pitch[current_idx] if current_idx < len(refined_pitch) else 0
        ui_pitch_label.set_text(f"Pitch: {live_pitch_val:.1f} Hz" if live_pitch_val > 30 else "Pitch: 0.0 Hz")

        current_time_ms = current_time_sec * 1000
        display_speaker = "Silence"
        display_rate = 0.0
        
        for segment in utterance_segments:
            if segment['start'] <= current_time_ms <= segment['end']:
                speaker_info = segment.get('speaker', {})
                display_speaker = f"Speaker: {speaker_info.get('name', 'Unknown')}"
                display_rate = segment['calculated_rate'] + np.random.uniform(-0.1, 0.1)
                break

        ui_speaker_label.set_text(display_speaker)
        ui_rate_label.set_text(f"Rate: {display_rate:.2f} cps" if display_rate > 0 else "Rate: 0.00 cps")

        return line_waveform, line_pitch_graph, line_rate_graph, ui_speaker_label, ui_pitch_label, ui_rate_label

    print(f"영상 인코딩 시작 (총 프레임: {TOTAL_FRAMES})...")
    writer = FFMpegWriter(fps=FPS, metadata=dict(artist='SpeechAnalyzer'), bitrate=2000)
    
    with writer.saving(fig, OUTPUT_VIDEO_PATH, dpi=100):
        for i in range(TOTAL_FRAMES):
            update_frame(i)
            writer.grab_frame()
            if i % 100 == 0:
                print(f"진행률: {i}/{TOTAL_FRAMES} frames")

    plt.close()
    print(f"저장이 완료되었습니다: {os.path.abspath(OUTPUT_VIDEO_PATH)}")
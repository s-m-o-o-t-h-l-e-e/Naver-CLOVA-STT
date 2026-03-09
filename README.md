# 🎙️ AI Voice Analysis & Automation System

> **Naver CLOVA STT**와 **고정밀 음향 분석 알고리즘**을 결합하여, 음성 데이터로부터 텍스트와 핵심 음향 지표(Pitch, CPS)를 자동 추출하고 시각화하는 통합 연구 솔루션입니다.  

<br>

## 📋 주요 기능

### 🛍️ 사용자 경험 (UX)
* **One-Stop 대시보드**: Streamlit 기반 인터페이스로 파일 업로드부터 결과 확인까지 한 번에 수행 
* **실시간 상태 표시**: 분석 단계별 프로그레스 바 및 상태 메시지 제공 
* **다양한 포맷 내보내기**: 분석 결과물(TXT, JSON, TSV) 및 자막 파일(SRT, VTT), 데이터 보고서(CSV) 다운로드 지원 
* **동적 시각화**: 파형(Waveform)과 피치 트래킹 그래프를 대시보드 내 실시간 출력

---

### ⚙️ 백엔드 및 핵심 엔진
* **최적 STT 엔진**: OpenAI Whisper 대비 한국어 구어체 인식률과 정밀도가 우수한 **Naver CLOVA Speech** 최종 채택 
* **고정밀 Pitch 추출**: PyWorld(Stonemask/Dio) 알고리즘을 활용해 안정적인 F0(기본 주파수) 값 확보 
* **발화 속도(CPS) 산출**: 에너지 엔벨로프 분석 및 STT 타임스탬프 연산을 통해 초당 음절 수 자동 계산 
* **자동 인코딩 파이프라인**: FFmpeg를 활용하여 분석 수치(Hz, CPS)가 실시간 오버레이된 **.mp4 영상 자동 생성** 

<br>

## 🏗️ 프로젝트 구조

```text
VoiceAnalysis/
├── src/                          # 메인 소스 코드
│   ├── Streamlit(Include Download).py    # [Web] 풀기능 통합 대시보드 (다운로드 포함)
│   ├── Streamlit(Exclude Download).py    # [Web] 웹 기반 실시간 분석 시각화 인터페이스
│   ├── Naver CLOVA STT(Include mp4 conversion).py # [Core] 분석 영상(.mp4) 생성 모듈
│   └── Naver CLOVA STT(Exclude mp4 conversion).py # [Core] 실시간 애니메이션 시각화 모듈
├── output/                       # 분석 결과물 저장 폴더 (.mp4, .srt, .json 등)
├── requirements.txt              # 핵심 라이브러리 의존성 정의
└── README.md                     # 프로젝트 가이드라인





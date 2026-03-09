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

승우님, 죄송합니다! 시스템 아키텍처 섹션부터 마지막까지 이미지에서 보여주신 것과 같은 회색 인용 박스, 구분선, 강조 기호를 적용하여 단 한 번에 복사할 수 있게 정리해 드립니다.

아래 내용을 복사해서 README의 ## 🏗️ 프로젝트 구조 다음 부분에 붙여넣으세요.

Markdown
<br>

## 📡 시스템 아키텍처

> [cite_start]본 시스템은 오디오 입력부터 최종 분석 영상 출력까지 전 과정을 자동화한 파이프라인으로 구성되어 있습니다. [cite: 33, 60] [cite_start]사용자가 파일을 업로드하면 STT 엔진과 음향 분석 엔진이 병렬적으로 구동되어 데이터를 통합합니다. [cite: 66]



1. **Input**: [cite_start]사용자가 MP3/WAV 오디오 파일 업로드 [cite: 33]
2. **Analysis**: 
   * **STT**: [cite_start]Naver CLOVA API를 호출하여 고정밀 텍스트 및 구간별 시간 정보(Timestamp) 획득 [cite: 57, 64]
   * **Acoustic**: [cite_start]PyWorld(Stonemask/Dio) 알고리즘으로 Pitch(Hz) 및 CPS(Speech Rate) 데이터 정밀 산출 [cite: 30, 35]
3. **Synthesis**: [cite_start]분석 데이터를 FFmpeg를 활용해 프레임 단위로 결합하여 실시간 수치가 포함된 시각화 영상 렌더링 [cite: 33, 60]
4. **Output**: [cite_start]Streamlit 웹 화면 출력 및 6종의 분석 결과 파일(JSON, CSV, SRT 등) 패키징 제공 [cite: 30, 66]

---

## 📈 모델 비교 분석 및 성과

### STT 모델 비교
| 모델명 | 한국어 인식 정확도 | 처리 속도 | 타임스탬프 정밀도 | 비고 |
| :--- | :---: | :---: | :---: | :--- |
| **Whisper(Local)** | 보통 | 느림 | 낮음 | [cite_start]로컬 자원 소모가 큼 [cite: 53, 61] |
| **Faster-Whisper** | 높음 | 빠름 | 보통 | [cite_start]GPU 가속(CUDA) 적용 [cite: 54, 63] |
| **CLOVA Speech** | **최상** | **매우 빠름** | **매우 높음** | [cite_start]**최종 선정 모델** [cite: 56, 59] |

### 정량적 성과 (기존 방식 대비)
* **분석 소요 시간**: [cite_start]음성 파일 10분 기준 약 3분 → **약 10초 (약 95% 단축)** [cite: 38, 68]
* **데이터 객관성**: [cite_start]분석가의 주관적 해석을 배제하고 알고리즘 기반의 정량적 수치 제공 [cite: 40, 69]
* **사용 편의성**: [cite_start]복잡한 라이브러리 숙련 없이 웹 대시보드를 통해 누구나 고도화된 분석 기능 활용 가능 [cite: 70]

---

## 🎨 시각화 가이드 (Visualization)
* **Waveform (파형)**: `#1DB954` (Green) - [cite_start]실시간 음성 신호의 진폭 시각화 [cite: 29]
* **Pitch (피치)**: `#FFD700` (Gold) - [cite_start]발화의 높낮이(Hz) 변화 정밀 트래킹 [cite: 29, 35]
* **Speech Rate (속도)**: `#00BFFF` (Blue) - [cite_start]실시간 CPS(초당 음절 수) 수치 출력 [cite: 30, 35]



---

**Main Researcher**: 컴퓨터공학과 이승우 (202305129)
**Affiliation**: ㈜코드데이원 (인턴십 프로젝트)

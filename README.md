# YouTube → 한국어 음성 변환기

YouTube 영어 영상을 한국어 음성으로 변환하는 Python 프로젝트입니다.

## 대상 채널
https://youtube.com/@bitemegames?si=xJN10a9C5GS53KUb

## 프로젝트 목표
영어로 된 YouTube 영상을 다음 과정을 통해 한국어 음성으로 변환:
1. YouTube 영상에서 오디오 추출
2. 오디오를 영어 텍스트로 변환 (STT)
3. 영어 텍스트를 한국어로 번역
4. 한국어 텍스트를 음성으로 변환 (TTS)

## 사용 기술 스택 (100% 무료 오픈소스)

### 1. YouTube 오디오 추출
- **yt-dlp**: YouTube 동영상에서 오디오 추출

### 2. 음성-텍스트 변환 (STT)
- **OpenAI Whisper**: 고품질 무료 음성 인식

### 3. 번역
- **Argos Translate**: 완전 무료 오픈소스 번역 엔진

### 4. 텍스트-음성 변환 (TTS)
- **gTTS (Google Text-to-Speech)**: 무료 한국어 TTS

## 설치 및 사용법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 사용법
```bash
python youtube2korean.py "YouTube_URL"
```

## 프로젝트 구조
```
youtube2korean/
├── README.md
├── requirements.txt
├── youtube2korean.py    # 메인 스크립트
├── audio/              # 추출된 오디오 파일
├── text/               # 변환된 텍스트 파일
└── output/             # 최종 한국어 음성 파일
```

## 기능
- YouTube URL에서 자동 오디오 추출
- 고품질 영어 음성 인식 (Whisper)
- 오프라인 영어→한국어 번역 (Argos)
- 자연스러운 한국어 TTS 생성
- 배치 처리 지원
- 진행 상황 표시
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

## 사용 기술 스택 (100% 무료 로컬 실행)

### 1. YouTube 오디오 추출
- **yt-dlp**: YouTube 동영상에서 오디오 추출
- **FFmpeg**: 오디오 후처리 및 변환

### 2. 음성-텍스트 변환 (STT)
- **OpenAI Whisper**: 고품질 무료 음성 인식

### 3. 번역
- **Ollama + Gemma 3:4B**: 로컬 실행 대화형 AI 모델을 통한 자연스러운 번역
- 완전 오프라인 실행으로 프라이버시 보장
- 컨텍스트를 고려한 고품질 번역

### 4. 텍스트-음성 변환 (TTS)
- **gTTS (Google Text-to-Speech)**: 무료 한국어 TTS

## 설치 및 사용법

### 1. 사전 요구사항
#### FFmpeg 설치
```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

#### Ollama 설치 및 Gemma 모델 다운로드
```bash
# Ollama 설치 (https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh

# Ollama 서버 시작
ollama serve

# 새 터미널에서 Gemma 3:4B 모델 다운로드
ollama pull gemma2:9b
# 또는 더 작은 모델을 원한다면
ollama pull gemma2:2b
```

### 2. Python 의존성 설치
```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 사용법
```bash
# 가상환경 활성화
source venv/bin/activate

# YouTube 영상 변환
python youtube2korean.py "YouTube_URL"

# 출력 파일명 지정
python youtube2korean.py "YouTube_URL" -o "my_audio.mp3"

# 출력 디렉토리 지정
python youtube2korean.py "YouTube_URL" --output-dir "custom_output"
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

## 주요 기능
- ✅ YouTube URL에서 자동 오디오 추출 (yt-dlp + FFmpeg)
- ✅ 고품질 영어 음성 인식 (OpenAI Whisper)
- ✅ 로컬 AI 모델을 통한 자연스러운 번역 (Ollama + Gemma)
- ✅ 한국어 텍스트-음성 변환 (gTTS)
- ✅ 청크 단위 처리로 안정성 보장
- ✅ 재시도 로직으로 오류 복구
- ✅ 상세한 진행 상황 표시
- ✅ 완전 오프라인 실행 (gTTS 제외)

## 개선 사항 (v2.0)
- 🔄 MarianMT → Ollama + Gemma 모델로 번역 엔진 교체
- 🛠️ FFmpeg 의존성 추가로 오디오 처리 안정성 향상
- 🔁 재시도 로직 및 에러 처리 강화
- 📊 더 상세한 로깅 및 진행 상황 표시
- ⚡ 청크 크기 최적화로 메모리 사용량 개선

## 문제 해결
### Ollama 연결 오류
```bash
# Ollama 서버 재시작
pkill ollama
ollama serve
```

### FFmpeg 오류
```bash
# FFmpeg 설치 확인
ffmpeg -version

# macOS에서 재설치
brew reinstall ffmpeg
```

### 번역이 중단되는 경우
- 청크 크기가 자동으로 500자로 제한됨
- 최대 3번 재시도 후 원본 텍스트 사용
- Ollama 모델 메모리 부족 시 더 작은 모델 사용 권장

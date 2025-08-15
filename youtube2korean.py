#!/usr/bin/env python3
"""
YouTube → 한국어 음성 변환기
YouTube 영어 영상을 한국어 음성으로 변환하는 스크립트
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path
from typing import Optional
import yt_dlp
import whisper
import ollama
from gtts import gTTS
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTube2Korean:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.audio_dir = Path("audio")
        self.text_dir = Path("text")
        
        # 디렉토리 생성
        for dir_path in [self.output_dir, self.audio_dir, self.text_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Whisper 모델 로드
        logger.info("Whisper 모델 로딩 중...")
        self.whisper_model = whisper.load_model("base")
        
        # Ollama 번역 모델 초기화 (Gemma 3:4B 사용)
        self._setup_ollama_model()
    
    def _setup_ollama_model(self):
        """Ollama 번역 모델 설정 - Gemma 3:4B 사용"""
        logger.info("Ollama 연결 확인 중...")
        
        self.ollama_model = "gemma3:4b"  # Gemma 모델 사용
        
        try:
            # Ollama 서비스 확인
            models = ollama.list()
            print('===models',models)
            available_models = [model['model'] for model in models['models']]
            print("available_models",available_models)
            if self.ollama_model not in available_models:
                logger.warning(f"모델 {self.ollama_model}을 찾을 수 없습니다.")
                logger.info(f"사용 가능한 모델: {available_models}")
                # Gemma 모델 중 사용 가능한 것 찾기
                gemma_models = [m for m in available_models if 'gemma' in m.lower()]
                if gemma_models:
                    self.ollama_model = gemma_models[0]
                    logger.info(f"대신 {self.ollama_model} 모델을 사용합니다.")
                else:
                    logger.error("사용 가능한 Gemma 모델이 없습니다.")
                    self.ollama_model = None
                    return
            
            logger.info(f"Ollama 번역 모델 준비 완료: {self.ollama_model}")
            
        except Exception as e:
            logger.error(f"Ollama 연결 실패: {e}")
            logger.info("번역 기능을 건너뛰고 원본 텍스트를 사용합니다.")
            self.ollama_model = None
    
    def extract_audio(self, youtube_url: str) -> Optional[str]:
        """YouTube에서 오디오 추출"""
        logger.info(f"YouTube 오디오 추출 시작: {youtube_url}")
        
        # 임시 파일명 생성
        temp_file = self.audio_dir / "temp_audio"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(temp_file) + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # 추출된 파일 찾기
            audio_file = temp_file.with_suffix('.wav')
            if audio_file.exists():
                logger.info(f"오디오 추출 완료: {audio_file}")
                return str(audio_file)
            else:
                logger.error("오디오 파일을 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"오디오 추출 실패: {e}")
            return None
    
    def transcribe_audio(self, audio_file: str) -> Optional[str]:
        """오디오를 텍스트로 변환 (STT)"""
        logger.info("음성 인식 시작...")
        
        try:
            result = self.whisper_model.transcribe(audio_file, language="en")
            text = result["text"].strip()
            
            # 텍스트 파일로 저장
            text_file = self.text_dir / "transcribed_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"음성 인식 완료. 텍스트 길이: {len(text)} 문자")
            logger.info(f"텍스트 저장됨: {text_file}")
            
            return text
            
        except Exception as e:
            logger.error(f"음성 인식 실패: {e}")
            return None
    
    def translate_text(self, english_text: str) -> Optional[str]:
        """영어 텍스트를 한국어로 번역 (Ollama 사용)"""
        logger.info("Ollama를 사용한 번역 시작...")
        
        try:
            if self.ollama_model is None:
                logger.warning("Ollama 모델이 없어 원본 텍스트를 반환합니다.")
                return english_text
            
            # 텍스트를 청크 단위로 분할 (안정성을 위해 더 작은 청크 사용)
            chunks = self._split_text(english_text, max_length=500)
            translated_chunks = []
            
            for i, chunk in enumerate(tqdm(chunks, desc="Ollama 번역 진행")):
                max_retries = 3
                retry_count = 0
                translated = None
                
                while retry_count < max_retries and translated is None:
                    try:
                        logger.info(f"청크 {i+1}/{len(chunks)} 번역 중... (시도: {retry_count+1})")
                        
                        # Ollama를 사용한 번역
                        prompt = f"""다음 영어 텍스트를 자연스러운 한국어로 번역해주세요. 간결하고 정확하게 번역해주세요.

영어: {chunk}

한국어:"""

                        response = ollama.chat(
                            model=self.ollama_model,
                            messages=[{
                                'role': 'user',
                                'content': prompt
                            }],
                            options={
                                'temperature': 0.2,  # 더 일관성 있는 번역
                                'top_p': 0.8,
                                'num_predict': 1024,  # 토큰 수 줄임
                                'num_ctx': 2048      # 컨텍스트 줄임
                            },
                            keep_alive='10m'
                        )
                        
                        translated = response['message']['content'].strip()
                        logger.info(f"청크 {i+1} 번역 완료")
                        break
                        
                    except Exception as e:
                        retry_count += 1
                        logger.warning(f"청크 {i+1} 번역 실패 (시도 {retry_count}/{max_retries}): {e}")
                        if retry_count < max_retries:
                            import time
                            time.sleep(2)  # 2초 대기 후 재시도
                
                if translated is not None:
                    translated_chunks.append(translated)
                else:
                    logger.error(f"청크 {i+1} 번역 최종 실패, 원본 텍스트 사용")
                    translated_chunks.append(chunk)  # 원본 텍스트 사용
            
            korean_text = " ".join(translated_chunks)
            
            # 번역된 텍스트 저장
            korean_file = self.text_dir / "translated_text.txt"
            with open(korean_file, 'w', encoding='utf-8') as f:
                f.write(korean_text)
            
            logger.info(f"번역 완료. 한국어 텍스트 길이: {len(korean_text)} 문자")
            logger.info(f"번역 텍스트 저장됨: {korean_file}")
            
            return korean_text
            
        except Exception as e:
            logger.error(f"번역 실패: {e}")
            return None
    
    def _split_text(self, text: str, max_length: int = 1000) -> list:
        """텍스트를 적절한 크기로 분할"""
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def text_to_speech(self, korean_text: str, output_filename: str = "korean_audio.mp3") -> Optional[str]:
        """한국어 텍스트를 음성으로 변환 (TTS)"""
        logger.info("TTS 변환 시작...")
        
        try:
            # 텍스트를 청크로 분할 (gTTS 길이 제한)
            chunks = self._split_text(korean_text, max_length=500)
            
            if len(chunks) == 1:
                # 단일 파일 생성
                tts = gTTS(text=korean_text, lang='ko', slow=False)
                output_path = self.output_dir / output_filename
                tts.save(str(output_path))
                logger.info(f"TTS 완료: {output_path}")
                return str(output_path)
            else:
                # 여러 청크를 개별 파일로 저장
                audio_files = []
                for i, chunk in enumerate(tqdm(chunks, desc="TTS 진행")):
                    tts = gTTS(text=chunk, lang='ko', slow=False)
                    chunk_file = self.output_dir / f"chunk_{i:03d}.mp3"
                    tts.save(str(chunk_file))
                    audio_files.append(str(chunk_file))
                
                logger.info(f"TTS 완료: {len(audio_files)}개 파일 생성")
                return audio_files[0]  # 첫 번째 파일 경로 반환
                
        except Exception as e:
            logger.error(f"TTS 변환 실패: {e}")
            return None
    
    def process_youtube_video(self, youtube_url: str, output_filename: str = "korean_audio.mp3") -> bool:
        """전체 파이프라인 실행"""
        logger.info("=== YouTube → 한국어 음성 변환 시작 ===")
        
        # 1. 오디오 추출
        audio_file = self.extract_audio(youtube_url)
        if not audio_file:
            return False
        
        # 2. 음성 인식
        english_text = self.transcribe_audio(audio_file)
        if not english_text:
            return False
        
        # 3. 번역
        korean_text = self.translate_text(english_text)
        if not korean_text:
            return False
        
        # 4. TTS
        output_file = self.text_to_speech(korean_text, output_filename)
        if not output_file:
            return False
        
        logger.info("=== 변환 완료! ===")
        logger.info(f"최종 출력 파일: {output_file}")
        
        # 임시 오디오 파일 정리
        try:
            os.remove(audio_file)
            logger.info("임시 파일 정리 완료")
        except:
            pass
        
        return True

def main():
    parser = argparse.ArgumentParser(description='YouTube 영상을 한국어 음성으로 변환')
    parser.add_argument('url', help='YouTube URL')
    parser.add_argument('-o', '--output', default='korean_audio.mp3', 
                       help='출력 파일명 (기본값: korean_audio.mp3)')
    parser.add_argument('--output-dir', default='output',
                       help='출력 디렉토리 (기본값: output)')
    
    args = parser.parse_args()
    
    if not args.url:
        print("YouTube URL을 입력해주세요.")
        sys.exit(1)
    
    # 변환기 초기화 및 실행
    converter = YouTube2Korean(output_dir=args.output_dir)
    success = converter.process_youtube_video(args.url, args.output)
    
    if success:
        print("✅ 변환이 성공적으로 완료되었습니다!")
    else:
        print("❌ 변환 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
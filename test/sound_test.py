import pygame
import time

# 초기화
pygame.mixer.init()

# 오디오 파일 로드 (MP3 또는 WAV)
audio_file = "audio/alert-ex.mp3"  # 내 mp3 파일의 상대경로
pygame.mixer.music.load(audio_file)

# 재생
pygame.mixer.music.play()

# 일정 시간 동안 실행(일단 기본 3초로 잡음)
time.sleep(3)  

# 종료
pygame.mixer.music.stop()

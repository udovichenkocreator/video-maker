#!/bin/bash

# Получаем параметры из переменных окружения
IMAGE_URL=$IMAGE_URL
AUDIO_URL=$AUDIO_URL
OUTPUT_FILENAME=$OUTPUT_FILENAME

# Скачиваем файлы
wget -O /app/input.jpg "$IMAGE_URL"
wget -O /app/input.mp3 "$AUDIO_URL"

# Генерируем видео
ffmpeg -loop 1 -i /app/input.jpg -i /app/input.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p \
  -shortest -y /app/$OUTPUT_FILENAME

# Выводим URL файла (для Make)
echo "VIDEO_URL=https://your-render-app.onrender.com/output.mp4"

# Копируем файл для доступа по HTTP
cp /app/$OUTPUT_FILENAME /app/output.mp4

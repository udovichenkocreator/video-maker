from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from moviepy.editor import ImageClip, AudioFileClip  # Используем editor
import uuid

app = FastAPI()

# Папка для хранения готовых видео
VIDEO_DIR = "/tmp/videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# Подключаем статические файлы
app.mount("/files", StaticFiles(directory=VIDEO_DIR), name="files")

@app.get("/wakeup")
async def wakeup():
    """
    Пробуждающий эндпоинт. Отправь любой GET-запрос сюда перед /merge.
    """
    return {"status": "ok", "message": "Service is awake!"}

@app.post("/merge")
async def merge(payload: dict):
    image_url = payload.get("image_url")
    audio_url = payload.get("audio_url")

    if not image_url or not audio_url:
        raise HTTPException(status_code=400, detail="image_url and audio_url required")

    job_id = str(uuid.uuid4())
    img_path = f"/tmp/{job_id}.jpg"
    aud_path = f"/tmp/{job_id}.mp3"
    out_path = f"{VIDEO_DIR}/{job_id}.mp4"  # Сохраняем в VIDEO_DIR

    try:
        # Скачиваем картинку
        with open(img_path, "wb") as f:
            f.write(requests.get(image_url).content)

        # Скачиваем аудио
        with open(aud_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        # Загружаем аудио, чтобы узнать длительность
        audio = AudioFileClip(aud_path)
        # Загружаем изображение
        image = ImageClip(img_path, duration=audio.duration)
        # Привязываем аудио
        final = image.set_audio(audio)

        # Экспортируем видео для YouTube Shorts
        final.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=f"/tmp/{job_id}_temp.mp4",
            remove_temp=True,
            logger=None,
            fps=30,
            audio_fps=44100,
            preset="medium",
            audio_bitrate="128k",
            bitrate="5000k",
            threads=2
        )

        # Генерируем URL
        video_url = f"https://video-maker-dnah.onrender.com/files/{job_id}.mp4"

        return {"url": video_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Очистка
        for f in [img_path, aud_path]:
            if os.path.exists(f):
                os.remove(f)
        # Не удаляем out_path — он нужен для доступа по URL

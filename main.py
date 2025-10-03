from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
import os
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import uuid

app = FastAPI()

@app.post("/merge")
async def merge(payload: dict):
    image_url = payload.get("image_url")
    audio_url = payload.get("audio_url")
    
    if not image_url or not audio_url:
        raise HTTPException(status_code=400, detail="image_url and audio_url required")

    job_id = str(uuid.uuid4())
    img_path = f"/tmp/{job_id}.jpg"
    aud_path = f"/tmp/{job_id}.mp3"
    out_path = f"/tmp/{job_id}.mp4"

    try:
        # Скачиваем картинку
        with open(img_path, "wb") as f:
            f.write(requests.get(image_url).content)
        
        # Скачиваем аудио
        with open(aud_path, "wb") as f:
            f.write(requests.get(audio_url).content)

       # Масштабируем изображение под вертикальный формат
        image = ImageClip(img_path).resize(height=1920).resize(width=1080)
        image.duration = min(30, audio.duration)
        
        # Привязываем аудио
        final = image.set_audio(audio).subclip(0, audio.duration)
        
        # Экспортируем с оптимизациями для YouTube Shorts
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

        return FileResponse(out_path, media_type="video/mp4", filename="output.mp4")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Очистка
        for f in [img_path, aud_path, out_path]:
            if os.path.exists(f):
                os.remove(f)

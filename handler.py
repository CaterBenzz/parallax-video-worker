import runpod
import requests
import base64
import time
import os

PARALLAX_CALLBACK_URL = os.getenv("PARALLAX_CALLBACK_URL")

def handler(job):
    job_id = job.get("id")
    payload = job.get("input", {})

    # --- SIMULIERTE VIDEO-GENERIERUNG (Platzhalter) ---
    time.sleep(2)
    fake_video_bytes = b"FAKE_VIDEO_DATA"
    video_base64 = base64.b64encode(fake_video_bytes).decode("utf-8")

    result = {
        "job_id": job_id,
        "status": "completed",
        "video_base64": video_base64
    }

    # --- CALLBACK ZU PARALLAX ---
    if PARALLAX_CALLBACK_URL:
        try:
            requests.post(
                PARALLAX_CALLBACK_URL,
                json=result,
                timeout=10
            )
        except Exception as e:
            print("Callback failed:", e)

    return result

runpod.serverless.start({"handler": handler})

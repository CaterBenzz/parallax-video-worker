import runpod
import requests
import base64
import time
import os
import json

PARALLAX_CALLBACK_URL = os.getenv("PARALLAX_CALLBACK_URL")

def handler(event):
    print("[PARALLAX] Raw event received:")
    print(json.dumps(event, indent=2))

    job_input = event.get("input", {})

    parallax_job_id = job_input.get("job_id")

    print("[PARALLAX] Parallax Job ID:", parallax_job_id)
    print("[PARALLAX] Callback URL:", PARALLAX_CALLBACK_URL)

    if not parallax_job_id:
        raise ValueError("No job_id provided by Parallax")

    # --- SIMULIERTE VIDEO-GENERIERUNG ---
    print("[PARALLAX] Generating video...")
    time.sleep(2)

    fake_video_bytes = b"FAKE_VIDEO_DATA"
    video_base64 = base64.b64encode(fake_video_bytes).decode("utf-8")

    payload = {
        "job_id": parallax_job_id,
        "status": "completed",
        "video_base64": video_base64
    }

    print("[PARALLAX] Sending callback payload:")
    print(json.dumps(payload, indent=2))

    if PARALLAX_CALLBACK_URL:
        response = requests.post(
            PARALLAX_CALLBACK_URL,
            json=payload,
            timeout=10
        )
        print("[PARALLAX] Callback response code:", response.status_code)
    else:
        print("[PARALLAX] ERROR: PARALLAX_CALLBACK_URL not set")

    return payload


runpod.serverless.start({
    "handler": handler
})

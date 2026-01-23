import runpod
import requests
import base64
import time
import os
import json

PARALLAX_CALLBACK_URL = os.getenv("PARALLAX_CALLBACK_URL")

def handler(job):
    print("[PARALLAX] Job received:")
    print(json.dumps(job, indent=2))

    job_input = job.get("input", {})
    job_id = job_input.get("job_id") or job.get("id")

    print(f"[PARALLAX] job_id = {job_id}")

    # --- SIMULIERTE VIDEO-GENERIERUNG ---
    print("[PARALLAX] Generating video...")
    time.sleep(2)

    fake_video_bytes = b"FAKE_VIDEO_DATA"
    video_base64 = base64.b64encode(fake_video_bytes).decode("utf-8")

    result = {
        "job_id": job_id,
        "status": "completed",
        "video_base64": video_base64
    }

    print("[PARALLAX] Generation done, sending callback...")

    # --- CALLBACK ---
    if PARALLAX_CALLBACK_URL:
        try:
            response = requests.post(
                PARALLAX_CALLBACK_URL,
                json=result,
                timeout=10
            )
            print("[PARALLAX] Callback response:", response.status_code)
        except Exception as e:
            print("[PARALLAX] Callback failed:", str(e))
    else:
        print("[PARALLAX] No PARALLAX_CALLBACK_URL set")

    return result


runpod.serverless.start({
    "handler": handler
})

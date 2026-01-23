import runpod
import base64
import time

print("[PARALLAX] Handler loading...")

def handler(event):
    print("[PARALLAX] Job received")
    
    job_input = event.get("input", {})
    job_id = job_input.get("job_id", "unknown")
    callback_url = job_input.get("callback_url", "")
    
    print(f"[PARALLAX] job_id={job_id}")
    
    # Simulate work
    time.sleep(2)
    
    # Minimal valid MP4
    mp4 = bytes([
        0x00,0x00,0x00,0x1C,0x66,0x74,0x79,0x70,
        0x69,0x73,0x6F,0x6D,0x00,0x00,0x02,0x00,
        0x69,0x73,0x6F,0x6D,0x69,0x73,0x6F,0x32,
        0x6D,0x70,0x34,0x31,0x00,0x00,0x00,0x08,
        0x66,0x72,0x65,0x65,0x00,0x00,0x00,0x00
    ])
    video_b64 = base64.b64encode(mp4).decode()
    
    # Send callback
    if callback_url:
        print(f"[PARALLAX] Sending callback to {callback_url}")
        try:
            import requests
            resp = requests.post(callback_url, json={
                "job_id": job_id,
                "status": "completed",
                "video_base64": video_b64
            }, timeout=30)
            print(f"[PARALLAX] Callback: {resp.status_code}")
        except Exception as e:
            print(f"[PARALLAX] Callback error: {e}")
    
    print("[PARALLAX] Done")
    return {"status": "success", "job_id": job_id, "video_base64": video_b64}

print("[PARALLAX] Starting worker...")
runpod.serverless.start({"handler": handler})

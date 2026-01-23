import runpod
import base64
import time
import os
import torch

print("[PARALLAX] Loading dependencies...")

from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
from diffusers.utils import export_to_video

PIPE = None

def load_model():
    global PIPE
    
    if PIPE is not None:
        return PIPE
    
    print("[PARALLAX] Loading AnimateDiff model...")
    start = time.time()
    
    adapter = MotionAdapter.from_pretrained(
        "guoyww/animatediff-motion-adapter-v1-5-3",
        torch_dtype=torch.float16
    )
    
    PIPE = AnimateDiffPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        motion_adapter=adapter,
        torch_dtype=torch.float16
    ).to("cuda")
    
    PIPE.scheduler = DDIMScheduler.from_config(PIPE.scheduler.config)
    PIPE.enable_vae_slicing()
    PIPE.enable_vae_tiling()
    
    print(f"[PARALLAX] Model loaded in {time.time()-start:.1f}s")
    
    return PIPE

def handler(event):
    print("[PARALLAX] Job received")
    
    job_input = event.get("input", {})
    job_id = job_input.get("job_id", "unknown")
    prompt = job_input.get("prompt", "a beautiful sunset")
    negative_prompt = job_input.get("negative_prompt", "")
    callback_url = job_input.get("callback_url", "")
    duration = job_input.get("duration", 5)
    fps = job_input.get("fps", 8)
    camera_motion = job_input.get("camera_motion", "none")
    motion_intensity = job_input.get("motion_intensity", 0.5)
    
    print(f"[PARALLAX] job_id={job_id}, prompt={prompt[:50]}...")
    
    try:
        pipe = load_model()
        
        num_frames = min(duration * fps, 32)
        
        motion_prompts = {
            "pan_left": ", smooth camera pan to the left",
            "pan_right": ", smooth camera pan to the right",
            "zoom_in": ", slow zoom in",
            "zoom_out": ", slow zoom out",
            "rotate_cw": ", rotating clockwise",
            "rotate_ccw": ", rotating counter-clockwise",
            "tilt_up": ", camera tilting upward",
            "tilt_down": ", camera tilting downward",
        }
        enhanced_prompt = prompt + motion_prompts.get(camera_motion, "")
        full_negative = negative_prompt + ", blurry, low quality, distorted"
        
        print(f"[PARALLAX] Generating {num_frames} frames...")
        start = time.time()
        
        output = pipe(
            prompt=enhanced_prompt,
            negative_prompt=full_negative,
            num_frames=num_frames,
            guidance_scale=7.5 + (motion_intensity * 2),
            num_inference_steps=25,
        )
        
        print(f"[PARALLAX] Generated in {time.time()-start:.1f}s")
        
        video_path = f"/tmp/{job_id}.mp4"
        export_to_video(output.frames[0], video_path, fps=fps)
        
        with open(video_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        
        os.remove(video_path)
        
        if callback_url:
            import requests
            requests.post(callback_url, json={
                "job_id": job_id,
                "status": "completed",
                "video_base64": video_b64
            }, timeout=60)
        
        return {"status": "success", "job_id": job_id, "video_base64": video_b64}
        
    except Exception as e:
        print(f"[PARALLAX] ERROR: {e}")
        if callback_url:
            import requests
            requests.post(callback_url, json={
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }, timeout=30)
        return {"status": "error", "job_id": job_id, "error": str(e)}

print("[PARALLAX] Starting worker...")
runpod.serverless.start({"handler": handler})

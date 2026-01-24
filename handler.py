import runpod
import base64
import time
import os
import sys

print("[PARALLAX] Worker starting...")

# Disable Intel XPU check
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

PIPE = None

def load_model():
    global PIPE
    
    if PIPE is not None:
        return PIPE
    
    print("[PARALLAX] Loading AnimateDiff...")
    start = time.time()
    
    import torch
    print(f"[PARALLAX] PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available")
    
    from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
    
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
    prompt = job_input.get("prompt", "a sunset")
    negative_prompt = job_input.get("negative_prompt", "")
    callback_url = job_input.get("callback_url", "")
    camera_motion = job_input.get("camera_motion", "none")
    motion_intensity = job_input.get("motion_intensity", 0.5)
    
    print(f"[PARALLAX] job_id={job_id}")
    
    try:
        pipe = load_model()
        
        from diffusers.utils import export_to_video
        
        motion_prompts = {
            "pan_left": ", smooth camera pan left",
            "pan_right": ", smooth camera pan right",
            "zoom_in": ", slow zoom in",
            "zoom_out": ", slow zoom out",
        }
        enhanced = prompt + motion_prompts.get(camera_motion, "")
        
        print(f"[PARALLAX] Generating 16 frames...")
        start = time.time()
        
        output = pipe(
            prompt=enhanced,
            negative_prompt=negative_prompt + ", blurry, low quality",
            num_frames=16,
            guidance_scale=7.5 + motion_intensity,
            num_inference_steps=20,
        )
        
        print(f"[PARALLAX] Done in {time.time()-start:.1f}s")
        
        video_path = f"/tmp/{job_id}.mp4"
        export_to_video(output.frames[0], video_path, fps=8)
        
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
        import traceback
        traceback.print_exc()
        if callback_url:
            import requests
            requests.post(callback_url, json={
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }, timeout=30)
        return {"status": "error", "job_id": job_id, "error": str(e)}

print("[PARALLAX] Starting runpod worker...")
runpod.serverless.start({"handler": handler})

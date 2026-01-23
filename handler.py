import runpod
import base64
import time
import os
import torch

print("[PARALLAX] Loading dependencies...")

from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
from diffusers.utils import export_to_video

# Global model - loaded once at cold start
PIPE = None

def load_model():
    """Load AnimateDiff model"""
    global PIPE
    
    if PIPE is not None:
        return PIPE
    
    print("[PARALLAX] Loading AnimateDiff model...")
    start = time.time()
    
    # Load motion adapter
    adapter = MotionAdapter.from_pretrained(
        "guoyww/animatediff-motion-adapter-v1-5-3",
        torch_dtype=torch.float16
    )
    
    # Load pipeline
    PIPE = AnimateDiffPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        motion_adapter=adapter,
        torch_dtype=torch.float16
    ).to("cuda")
    
    # Optimizations
    PIPE.scheduler = DDIMScheduler.from_config(PIPE.scheduler.config)
    PIPE.enable_vae_slicing()
    PIPE.enable_vae_tiling()
    
    # Optional: Enable memory efficient attention
    try:
        PIPE.enable_xformers_memory_efficient_attention()
        print("[PARALLAX] xformers enabled")
    except:
        print("[PARALLAX] xformers not available")
    
    print(f"[PARALLAX] Model loaded in {time.time()-start:.1f}s")
    
    # Warmup
    print("[PARALLAX] Warmup inference...")
    _ = PIPE(
        prompt="test",
        num_frames=8,
        num_inference_steps=5,
        guidance_scale=1.0,
    )
    print("[PARALLAX] Warmup complete")
    
    return PIPE

def handler(event):
    """Generate video from prompt"""
    print("[PARALLAX] Job received")
    
    job_input = event.get("input", {})
    job_id = job_input.get("job_id", "unknown")
    prompt = job_input.get("prompt", "a beautiful sunset")
    negative_prompt = job_input.get("negative_prompt", "")
    callback_url = job_input.get("callback_url", "")
    
    # Video settings
    duration = job_input.get("duration", 5)
    fps = job_input.get("fps", 8)  # AnimateDiff works best at 8fps
    camera_motion = job_input.get("camera_motion", "none")
    motion_intensity = job_input.get("motion_intensity", 0.5)
    
    print(f"[PARALLAX] job_id={job_id}")
    print(f"[PARALLAX] prompt={prompt[:80]}...")
    print(f"[PARALLAX] duration={duration}s, fps={fps}")
    
    try:
        # Load model
        pipe = load_model()
        
        # Calculate frames (AnimateDiff max ~32 frames)
        num_frames = min(duration * fps, 32)
        
        # Enhance prompt with camera motion
        motion_prompts = {
            "pan_left": ", smooth camera pan to the left",
            "pan_right": ", smooth camera pan to the right", 
            "zoom_in": ", slow zoom in, dolly forward",
            "zoom_out": ", slow zoom out, dolly backward",
            "rotate_cw": ", rotating view clockwise",
            "rotate_ccw": ", rotating view counter-clockwise",
            "tilt_up": ", camera tilting upward",
            "tilt_down": ", camera tilting downward",
        }
        enhanced_prompt = prompt + motion_prompts.get(camera_motion, "")
        
        # Default negative prompt
        full_negative = negative_prompt + ", blurry, low quality, distorted, watermark, text"
        
        print(f"[PARALLAX] Generating {num_frames} frames...")
        start = time.time()
        
        # Generate
        output = pipe(
            prompt=enhanced_prompt,
            negative_prompt=full_negative,
            num_frames=num_frames,
            guidance_scale=7.5 + (motion_intensity * 2),  # 7.5 - 9.5
            num_inference_steps=25,
        )
        
        gen_time = time.time() - start
        print(f"[PARALLAX] Generated in {gen_time:.1f}s")
        
        # Export to video
        video_path = f"/tmp/{job_id}.mp4"
        export_to_video(output.frames[0], video_path, fps=fps)
        
        # Read and encode
        with open(video_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        
        # Cleanup
        os.remove(video_path)
        
        print(f"[PARALLAX] Video: {len(video_b64)} chars base64")
        
        # Send callback
        if callback_url:
            print(f"[PARALLAX] Sending callback...")
            import requests
            resp = requests.post(callback_url, json={
                "job_id": job_id,
                "status": "completed", 
                "video_base64": video_b64
            }, timeout=60)
            print(f"[PARALLAX] Callback: {resp.status_code}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "frames": num_frames,
            "generation_time": gen_time,
            "video_base64": video_b64
        }
        
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

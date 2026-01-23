FROM runpod/pytorch:2.1.0-py3.10-cuda12.1.0-devel-ubuntu22.04

# Install dependencies
RUN pip install --no-cache-dir \
    runpod \
    requests \
    diffusers>=0.25.0 \
    transformers \
    accelerate \
    safetensors \
    xformers

# Pre-download models (optional - speeds up cold start)
RUN python -c "from diffusers import MotionAdapter; MotionAdapter.from_pretrained('guoyww/animatediff-motion-adapter-v1-5-3')"
RUN python -c "from diffusers import AnimateDiffPipeline; AnimateDiffPipeline.from_pretrained('runwayml/stable-diffusion-v1-5')"

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

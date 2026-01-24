FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

RUN pip install --no-cache-dir \
    runpod \
    requests \
    diffusers \
    transformers \
    accelerate \
    safetensors \
    imageio[ffmpeg]

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

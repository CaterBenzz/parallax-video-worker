FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

RUN pip install --no-cache-dir \
    runpod==1.6.0 \
    requests \
    numpy \
    huggingface_hub==0.20.0 \
    diffusers==0.25.0 \
    transformers==4.36.0 \
    accelerate==0.25.0 \
    safetensors \
    imageio[ffmpeg] \
    opencv-python-headless

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

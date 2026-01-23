FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

RUN pip install runpod requests diffusers transformers accelerate safetensors

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

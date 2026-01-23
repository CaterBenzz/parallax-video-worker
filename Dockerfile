FROM runpod/pytorch:2.1.0-py3.10-cuda12.1.0-devel-ubuntu22.04

RUN pip install --no-cache-dir \
    runpod \
    requests \
    diffusers \
    transformers \
    accelerate \
    safetensors

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

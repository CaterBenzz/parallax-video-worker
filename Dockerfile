FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

RUN pip install --no-cache-dir \
    runpod \
    requests \
    diffusers \
    transformers \
    accelerate \
    safetensors

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

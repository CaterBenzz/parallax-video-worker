FROM huggingface/diffusers-pytorch-cuda:latest

RUN pip install --no-cache-dir runpod requests

COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]

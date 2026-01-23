FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir runpod requests
COPY handler.py /app/handler.py
CMD ["python", "/app/handler.py"]

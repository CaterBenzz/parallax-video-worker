FROM python:3.10-slim

WORKDIR /app

COPY handler.py /app/handler.py

CMD ["python", "-c", "from handler import handler; print(handler({'input':'ping'}))"]

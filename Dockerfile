FROM python:3.10-slim

WORKDIR /app

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["python3", "app.py"]

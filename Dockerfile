FROM python:3.11-slim
RUN mkdir -p /files /app
RUN useradd pyuser
COPY . /app
RUN pip install -r /app/requirements.txt
RUN chown -R pyuser:pyuser /app
USER pyuser
WORKDIR /files
ENTRYPOINT ["python", "/app/main.py"]
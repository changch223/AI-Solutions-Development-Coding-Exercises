FROM python:3.9-slim
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 7860
ENTRYPOINT ["python3"]
CMD ["app.py"]

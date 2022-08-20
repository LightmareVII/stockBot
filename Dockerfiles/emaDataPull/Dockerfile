FROM python:3.8

VOLUME /stockBotData

COPY emaDataPull.py ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir alpaca-trade-api \
    pip install --no-cache-dir requests

CMD ["python", "./emaDataPull.py"]
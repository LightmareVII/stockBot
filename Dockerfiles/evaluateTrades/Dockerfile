FROM python:3.8

VOLUME /stockBotData

COPY evaluateTrades.py ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir alpaca-trade-api


CMD ["python", "./evaluateTrades.py"]
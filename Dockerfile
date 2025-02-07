FROM tensorflow/tensorflow:2.17.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN apt-get update && apt-get install -y libpulse0
RUN apt-get install -y python3-tk 
ENV DISPLAY=host.docker.internal:0
ENV PULSE_SERVER=host.docker.internal:4713
CMD ["python3", "main.py"]
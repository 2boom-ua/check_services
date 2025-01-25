FROM python:3.11-slim

WORKDIR /check_services

COPY . /check_services

RUN apt-get update && apt-get install -y procps git curl systemd dbus && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]

RUN pip install --no-cache-dir -r requirements.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD pgrep -fl check_services || exit 1

CMD ["python", "check_services.py"]


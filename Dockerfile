FROM python:3.11-slim

EXPOSE 8081

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/venv \
    HF_HOME=/models

RUN python -m venv "$VIRTUAL_ENV" && "$VIRTUAL_ENV/bin/pip" install --upgrade pip
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY pyproject.toml /app/
COPY run.py /app/
COPY src /app/src

RUN pip install --no-cache-dir .

RUN useradd --create-home --no-log-init --user-group wiki && \
    mkdir -p /models && chown -R wiki:wiki /app /models

USER wiki

CMD ["python", "run.py"]

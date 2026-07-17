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

# The cluster runs on CPU: pull the CPU-only torch wheel first, otherwise
# sentence-transformers drags the CUDA build in and the image blows past 15GB.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir .

RUN useradd --create-home --no-log-init --user-group wiki && \
    mkdir -p /models && chown -R wiki:wiki /app /models

USER wiki

CMD ["python", "run.py"]

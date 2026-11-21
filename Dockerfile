FROM python:3.15-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN pip install --no-cache-dir poetry==2.5.1
COPY pyproject.toml* poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload", "--reload-dir", "api"]

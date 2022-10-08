FROM python:3.9-slim as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps
RUN pip install pipenv
WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime
WORKDIR /app
COPY --from=python-deps /app/.venv/. /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

ENTRYPOINT ["python", "main.py"]

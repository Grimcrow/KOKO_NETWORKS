ARG APP_DIR=/api/
ARG LOG_DIR=/tmp
ARG POETRY_VERSION=1.1.2


FROM python:3.7.9-slim AS system-build
LABEL maintainer="ben.waithaka.njoroge.ke@gmail.com"
RUN apt-get update && apt-get install --no-install-recommends --yes


FROM system-build AS poetry-build
ARG POETRY_VERSION
ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONHASHSEED=random \
	PIP_NO_CACHE_DIR=off \
	PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install "poetry==$POETRY_VERSION"

FROM poetry-build
ARG APP_DIR
WORKDIR ${APP_DIR}
COPY . ${APP_DIR}
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev --no-interaction --no-ansi

CMD python manage.py

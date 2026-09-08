# Reproducible environment for the GC-IR reference implementation.
#
#   docker build -t gcir .
#   docker run --rm gcir make reproduce
#
# The base image is pinned by digest so that a rebuild months from now resolves
# to the same bytes. Dependencies are pinned in requirements.lock.
#
# Determinism note: the container fixes LANG, LC_ALL, TZ and PYTHONHASHSEED so
# that the *baseline* environment is stated rather than inherited. The
# determinism experiment then deliberately varies all four, so the pinning is a
# declared starting point, not a way of avoiding the question.

FROM python:3.11.11-slim-bookworm@sha256:6ed5bff4d7d377e2a27d9285553b8c21cfccc4f00881de1b24c9bc8d90016e82

LABEL org.opencontainers.image.title="gc-ir-reference"
LABEL org.opencontainers.image.description="GC-IR Reference Implementation - reproducibility artifact for 'From Risk Register to Runtime Predicate'"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=UTC \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends make git locales tzdata \
 && sed -i '/en_US.UTF-8/s/^# //; /de_DE.UTF-8/s/^# //; /tr_TR.UTF-8/s/^# //; /ja_JP.UTF-8/s/^# //' /etc/locale.gen \
 && locale-gen \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /artifact

COPY requirements.lock ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.lock

COPY . .

# The Makefile targets shell out to .venv/bin/python; inside the container the
# interpreter is already the pinned one.
ENV PYTHON=python
RUN sed -i 's|^PY     := \$(VENV)/bin/python|PY     := python|' Makefile

RUN python -m pytest -q

CMD ["make", "reproduce"]

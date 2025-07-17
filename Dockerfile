# syntax=docker/dockerfile:labs

FROM python:alpine
WORKDIR /chess

COPY --parents chess tests __main__.py ./

ENTRYPOINT [ "python", "__main__.py" ]

# Base
FROM nvidia/cuda:12.5.1-cudnn-devel-rockylinux9 AS base
RUN dnf -y update;

# Dev deps
FROM base AS devel
RUN dnf -y install git python3.12 python3.12-pip python3.12-pip-wheel;

# Pulse audio
FROM devel AS pulse
RUN dnf -y install pulseaudio;

# RoboCapture app
FROM pulse AS setup
WORKDIR /usr/src/robocapture

COPY . .

RUN useradd -ms /bin/bash robocapture;
RUN chown robocapture:robocapture /usr/src/robocapture/.pip_cache;

USER robocapture
RUN pip3.12 install --cache-dir ./.pip_cache -r requirements.txt;

# App
FROM setup AS app
WORKDIR /usr/src/robocapture

EXPOSE 9001
EXPOSE 9002

CMD ["./run_docker"]

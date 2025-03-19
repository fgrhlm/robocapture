FROM nvidia/cuda:12.5.1-cudnn-devel-rockylinux9 AS base
RUN dnf -y update;

FROM base AS devel
RUN dnf -y install git python3.12 python3.12-pip python3.12-pip-wheel;

FROM devel AS pulse
RUN dnf -y install pulseaudio;

FROM pulse AS app
WORKDIR /usr/src/robocapture
COPY . .

RUN pip3.12 install --no-cache-dir -r requirements.txt;

EXPOSE 9001
EXPOSE 9002

CMD ["./run_server", "conf/default_video.json"]

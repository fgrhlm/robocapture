# RoboCapture

# What?

RoboCapture is a wrapper around a number of popular audio/video processing
modules that allows you to define and deploy multimedia processing
pipelines.

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
![pyver](https://badgen.net/badge/Python/3.12.5)
![docker](https://badgen.net/badge/docker/yes/green)

<hr>

# Installation

The recommended way to run RoboCapture is to use the docker method. If you wish
to run robocapture locally you can do so by following the local installation
method described below, however YMMV.

## Get to the source.

Clone this repo to a suitable place in your filesystem:

`git clone https://github.com/fgrhlm/robocapture.git`

<hr>

## GPU Acceleration {#install-gpu}

Some of the included workers make use of 3rd party libraries that supports accelerated
processing by using GPU resources. To leverage this functionality in your pipelines
you need to have a supported GPU and the necessary software installed. RoboCapture is
developed and tested on an extremely limited number of hardware configurations. At
the moment, compatibility testing is only being done on nvidia platforms.

### Nvidia

If your systems package repository includes `cuDNN == 9.3` and `cuda == 12.5`, go ahead
and use your package manager to install those. If not then you can install them manually:

#### cuDNN

Download the [binaries](https://developer.nvidia.com/cudnn-9-3-0-download-archive).
Install using [instructions](https://developer.nvidia.com/cudnn-9-3-0-download-archive).

### cuda

Download the [binaries](https://developer.nvidia.com/cuda-12-5-0-download-archive).
Install using [instructions](https://docs.nvidia.com/cuda/archive/12.5.0/cuda-installation-guide-linux/index.html).

#### Nvidia Container Toolkit (Needed for docker gpu passthrough)

Follow installation instructions [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

<hr>

## Linux {#install-linux}

### Python

RoboCapture expects python version `3.12.5`. If your distro does not
provide a package for this specific version (it probably does not) you
can use one of the following methods to obtain the correct version:

#### Using pyenv (recommended)

Install pyenv following the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv)

1. Navigate to source directory `cd robocapture/`

2. Get python 3.12.9 `pyenv install 3.12.9`

3. Robocapture ships with a `.python-version` file which should allow pyenv to automatically switch
to the correct python version when in the source directory. You can test that your environment
is using the correct py version by (while in source directory) running `python --version` and verifying
that the output reads `Python 3.12.9`

#### Manual Installation

Follow official instructions [here](https://www.python.org/downloads/release/python-3129/)

#### Building from source

Follow official instructions [here](https://docs.python.org/3.12/using/unix.html#building-python)

#### Create and activate virtualenv

`python -m venv venv && source venv/bin/activate`

#### Install python dependencies

`pip install -r requirements.txt`

<hr>

## Docker {#install-docker}

Install and configure docker follow these [instructions](https://www.docker.com/get-started/)

If you intend to run GPU accelerated workers make sure you've looked at [Docs / Installation / GPU Acceleration](#install-gpu).

1. Build the image: `docker compose build`

<hr>

## Robot Operating System (ROS)

**WIP**

<hr>

# Configuration

## General

```

server_type    | The base worker. Can be "audio" or "video".
device         | Base worker input device.

```

_See [Docs / Config / External Workers](#config-workers)


```

on_data        | List of workers to be called when base worker has new data.
on_save        | List of workers to be called when base worker writes to the filesystem.
on_trigger_in  | List of workers to be called when base worker "trigger" is set.
on_trigger_out | List of workers to be called when base worker "trigger" is unset.

```

_See [Docs / Config / Socket](#config-socket)_

```

socket         | WebSocket config.

```

_See [Docs / Config / Logging](#config-logging)_

```

log            | Log config.

```

## Audio

_See [python-sounddevice.readthedocs.io](https://python-sounddevice.readthedocs.io/en/0.5.1/api/raw-streams.html#sounddevice.RawInputStream)_

```

sample_rate    | Stream sample rate.
channels       | Stream channels.
blksize        | Stream block size.

mode           | The capture mode. Can be "voice_activity" or "normal".
rec_threshold  | (Only in "activity" mode) The input-level at which capturing is triggered.
rec_hold       | (Only in "activity" mode) How long the capture should continue after activity stops.
max_clip_len   | Maximum clip length (in seconds).

```

## Video

```

img_w          | Output frame width.
img_h          | Output frame height.
img_color      | Output frame color mode.

```

## External Worker {#config-workers}

```

enabled        | On/Off.
name           | Name of the worker.
path           | Path to the worker .py source file.
config         | Config to pass into worker.

```

## Socket {#config-socket}

```

host           | Hostname.
port           | Port.

```

## Logging {#config-logging}

```

logLevel       | Log verbosity.


```

## YOLO

Options in this section are explained further [here](https://docs.ultralytics.com/modes/predict/#inference-arguments).

```

model_format   | Model format. Can be "onnx", "openvino", "tensor_rt" or "tflite"
weights        | Model weights.
min_conf       | Minimum detection confidence.
img_size       | Input Image Size.
stream         | Enables optimized processing of long videos or large batches.
verbose        | Enables debugging output during inference.
half           | Enables FP16 inference.
max_detect     | Max. amount of detections per image.
vid_stride     | Skip `n` amount of frames.
export_config  | Config for export formats.

```

For more information on `export_config` options look [here](https://docs.ultralytics.com/modes/export/#export-formats)

Example:

```

export_config = {
    "onnx": { "simplify": true, "half": true, "nms": true},
    "openvino": { "half": false, "nms": true, "int8": true, "data": "coco8.yaml"},
    "tensor_rt": { "simplify": true, "half": false, "nms": true, "int8": true, "data": "coco8.yaml"},
    "tflite": { "half": false, "nms": true, "int8": true, "data": "coco8.yaml"}
}

```

## Yunet

Options in this section are explained further [here](https://docs.opencv.org/4.x/df/d20/classcv_1_1FaceDetectorYN.html)

```

img_size       | Input Image Size.
weights        | Model weights.
cpu            | Force cpu inference.
img_size       | Input Image Size.
min_detect     | Minimum detection confidence.
max_nms        | Suppress bounding bouxes of IoU > than `n`
top_k          | Keep top K bounding boxes before NMS.

```

## Whisper

```

weights        | Model Weights.

```

<hr>

# Running

## Linux

First make sure you've followed all necessary steps in [Docs / Installation / Linux](#install-linux) and then:

1. Activate venv: `source venv/bin/activate`
2. Run: `python run_server <path-to-config>`

## Docker

Make sure you've followed all necessary steps in [Docs / Installation / Docker](#install-docker) and then:

1. Inside repo root: `docker compose up`

## ROS

Make sure you've followed all necessary steps in [Docs / Installation / ROS](#install-ros) and then:

# Usage

Pipeline results can be accessed in the ways listed below. Please refer to individual workers
documentation for details on output formatting for that specific worker. Reference clients and demos
are included in `client/{python,js}/demos`.

## WebSocket

Python:

```python

from asyncio import run
from websockets.asyncio.client import connect

rc_host = "127.0.0.1"
rc_port = 9002

# Connect to websocket.
async def client():
    async with connect(f"ws://{rc_host}:{rc_port}") as socket:
        while True:
            # Do something with the data
            msg = await websocket.recv()
            print(msg)

run(client())

```

Javascript (Not using robocapture.js):

```xml

const host = "127.0.0.1"; // RoboCapture Server Hostname
const port = 9002;        // RoboCapture Server Port

// Connect to RoboCapture Server.
const socket = new WebSocket(`ws://${host}:${port}`);

// Do something with the data.
socket.addEventListener("message", e => {
    console.log(e);
});

```

Javascript (Using robocapture.js):

```xml

import { Client, Hooks, Callback } from "/js/robocapture.js";

const host = "127.0.0.1"; // RoboCapture Server Hostname
const port = 9002;        // RoboCapture Server Port

const printMessage = (e) => {
    console.log(JSON.parse(e.data));
}

const audioClient = new Client("localhost", 9001, Array(
    new Callback(Hooks.MESSAGE, printMessage)
));

```

## ROS

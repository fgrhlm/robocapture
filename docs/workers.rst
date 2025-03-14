Workers
=======

Workers are instances that sits in the pipeline and performs
operations on the input data.

RoboCapture comes with a few predefined pipeline workers:
    Object Detection:
        - :doc:`yolo` - Object detection
        - :doc:`yunet`- Face detection

    Speech analysis:
        - :doc:`whisper` - Speech to Text

    Misc:
        - :doc:`frameb64` - base64 encodes a frames.
        - :doc:`meta_audio` - Gathers metadata from audiostream.
        - :doc:`meta_video` - Gathers metadata from videostream.

.. autosummary::
   :toctree: generated

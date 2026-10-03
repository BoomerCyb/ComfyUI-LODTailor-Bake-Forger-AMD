# AMD changes

Blender executable discovery and HIP device reporting are retained. Blender
provides Cycles HIP; no custom Torch GPU extension is built.

Installation uses ComfyUI's ROCm Python through install.py. Native extensions
use PyTorch architecture targeting without a card-specific build layer.
Tested on RX 9070 XT; other supported ROCm devices require validation.
Original licenses, algorithms and node registrations are preserved.

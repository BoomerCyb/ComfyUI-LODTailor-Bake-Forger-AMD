# ComfyUI-LODTailor-Bake-Forger-AMD — Windows AMD / RX 9070 XT

## ComfyUI ROCm installation video

For a visual walkthrough of installing ComfyUI with ROCm, watch
[TechChuckle — How to Run ComfyUI on ANY AMD GPU ROCm Setup + Image Generation Guide](https://www.youtube.com/watch?v=6LOqJdKe6zI&t=219s).
The link opens at **3:39**.

**To install the version used for these nodes, follow
[the tested ComfyUI ROCm setup guide](TESTED_ROCM_SETUP.md).** It includes the
recorded ComfyUI revision, pinned AMD runtime packages, a copy-and-paste version
check, and the node installation steps for **RX 9070 XT / gfx1201**.

The tested runtime is Python **3.12.9**, Torch
**2.15.0a0+rocm10.2.0a20260926**, HIP **7.17.26384**, and ROCm SDK **10.2**.
The installer normally selects newer nightly packages, so the video alone does
not guarantee these versions. Use the pinned setup guide before installing the
precompiled nodes, then complete the node's `PRECOMPILED_INSTALL.txt` steps.

## Download and install

**Use the green Code button → Download ZIP. This download contains the actual node files, full source and precompiled components.**

1. Close ComfyUI.
2. Download the ZIP and choose **Extract All** in Windows.
3. Open the extracted folder. It must contain `__init__.py` directly inside it.
4. Move any previous copy of this node outside `custom_nodes` to prevent duplicate nodes.
5. Move the extracted folder into your actual ComfyUI `custom_nodes` folder. You may rename it to `ComfyUI-LODTailor-Bake-Forger-AMD`.
6. Complete the setup below, then restart ComfyUI with its normal ROCm launcher.

```text
ComfyUI/
  custom_nodes/
    ComfyUI-LODTailor-Bake-Forger-AMD/
      __init__.py
      README.md
      PRECOMPILED_INSTALL.txt
      COMFYUI_ROCM_BUILD_GUIDE.md
```

There should be only one node folder level: `custom_nodes/node-folder/__init__.py`. Do not leave another extracted repository folder nested inside it.

## Required setup

Tested on **RX 9070 XT / gfx1201**, Windows x64, Python 3.12.9, Torch `2.15.0a0+rocm10.2.0a20260926`, HIP `7.17.26384`, ROCm SDK `10.2`.

Install Blender 5.2 separately, configure its path, and select HIP in the node. Follow PRECOMPILED_INSTALL.txt.

Read [PRECOMPILED_INSTALL.txt](PRECOMPILED_INSTALL.txt) for the exact remaining dependency/setup steps. Use ComfyUI’s Python, not a separate system Python. The included native modules do not need compilation in the tested environment. Python, Torch, ROCm, Blender and model weights are not bundled.

If your GPU or software environment differs, compatibility is not established. The precompiled files remain fixed gfx1201 builds.

## Experimental builds for other AMD GPUs

[Open the experimental builders and instructions](https://github.com/BoomerCyb/ComfyUI-LODTailor-Bake-Forger-AMD/tree/experimental-auto-arch). On that branch, use **Code -> Download ZIP** to get the experimental source, README, and build guide. The experimental source archive is also available in the release assets.

This separate source package detects the AMD GPU architecture and accepts an override. It requires building the native backends; it does not contain precompiled binaries for other GPUs. Do not install it alongside this tested copy in `custom_nodes`.

## Build details and attribution

- [ComfyUI ROCm build guide](COMFYUI_ROCM_BUILD_GUIDE.md)
- [AMD port notes](AMD_PORT.md)
- [Original node documentation](docs/SOURCE_README.md)
- [Release assets and validation](https://github.com/BoomerCyb/ComfyUI-LODTailor-Bake-Forger-AMD/releases)

AMD fork of [Mstafa-awad/LODTailor-Bake-Forger](https://github.com/Mstafa-awad/LODTailor-Bake-Forger). Original licenses and attribution are preserved. This repository is a fork of the original project with Windows AMD changes.

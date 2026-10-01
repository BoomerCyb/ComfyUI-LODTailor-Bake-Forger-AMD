# Bake Forger AMD support

## gfx1201 release scope

This release targets Windows AMD **gfx1201**, tested on **RX 9070 XT**.
The WTiVo, CuMesh and O-Voxel native builders retain their gfx1201 target;
they do not automatically rebuild for other GPU architectures. Support for other
AMD GPUs is not claimed. Bake Forger uses Blender device discovery and has no
custom native build; its validation in this release is also limited to RX 9070 XT.
Use the exact tested software environment described below and in AMD_PORT.md.

Use the existing ComfyUI Python dependencies listed in requirements.txt and install
Blender separately. The tested Blender version is 5.2. Place this repository folder
under custom_nodes and restart ComfyUI. Leave blender_exe blank, or set it to
blender/blender.exe, to discover Blender; an explicit Blender path is also accepted.
Select HIP for the Cycles device. The node logs the selected devices.

Validated on Windows 11, Python 3.12.9 and RX 9070 XT with ROCm Torch 10.2.
The actual six-map bake and GLB export passed at 64x64 and one sample, with hybrid
CPU disabled. Larger production bakes need validation on the user's meshes.
The output/latest directory is cleaned by the existing node; choose the output
folder deliberately. Original license and third-party notice files are retained.

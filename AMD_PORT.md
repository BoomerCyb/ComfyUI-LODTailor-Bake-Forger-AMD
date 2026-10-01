# Bake Forger AMD support

## Experimental architecture selection

This separate version detects an AMD GPU through the existing ROCm PyTorch
interpreter and builds for its reported architecture. Only RX 9070 XT / gfx1201
has prior native inference validation; other targets are experimental. Successful
architecture detection does not establish SDK support, compilation or inference
compatibility. Bake Forger continues to use Blender device discovery.

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

## Blender devices

Bake Forger has no native build script or architecture override. Its HIP devices are selected by Blender.

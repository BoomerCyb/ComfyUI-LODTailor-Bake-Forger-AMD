# Install the tested ComfyUI ROCm setup — RX 9070 XT / gfx1201

Watch [TechChuckle's ComfyUI ROCm installation video](https://www.youtube.com/watch?v=6LOqJdKe6zI&t=219s), starting at **3:39**, for the Windows installation walkthrough. Use the steps below to select the runtime versions used to build and test these AMD nodes.

## 1. Install ComfyUI ROCm in a new folder

Follow the prerequisites in [patientx-cfz/comfyui-rocm](https://github.com/patientx-cfz/comfyui-rocm), including Git and an appropriate AMD graphics driver. The recorded base revision is [`1020a8659495c597be98e27f5e645602fc92e261`](https://github.com/patientx-cfz/comfyui-rocm/commit/1020a8659495c597be98e27f5e645602fc92e261).

For a fresh installation, open PowerShell in the parent folder where you want ComfyUI installed and run:

```powershell
git clone https://github.com/patientx-cfz/comfyui-rocm.git ComfyUI-ROCm
Set-Location .\ComfyUI-ROCm
git checkout 1020a8659495c597be98e27f5e645602fc92e261
.\install.bat
```

Wait for installation to complete. The installer creates `python_env` and downloads the runtime. Its AMD package index changes over time, so complete step 2 before using these precompiled nodes. The checkout uses a fixed revision; running an updater can move away from it.

For an existing installation that already matches the versions below, go directly to step 3. Use a separate installation when trying to reproduce this setup rather than changing an environment you depend on.

## 2. Select the tested runtime versions

Close ComfyUI. Run these commands from your new `ComfyUI-ROCm` folder, using its own Python:

```powershell
@'
torch[device-gfx1201]==2.15.0a0+rocm10.2.0a20260926
torchvision[device-gfx1201]==0.30.0a0+rocm10.2.0a20260926
torchaudio==2.11.0.3+rocm10.2.0a20260927
amd-torch-device-gfx1201==2.15.0a0+rocm10.2.0a20260926
amd-torchvision-device-gfx1201==0.30.0a0+rocm10.2.0a20260926
rocm-sdk-core==10.2.0a20260926
rocm-sdk-libraries==10.2.0a20260926
rocm-sdk-devel==10.2.0a20260927
rocm-sdk-device-gfx1201==10.2.0a20260926
'@ | Set-Content -Encoding ascii .\tested-rocm-packages.txt

.\python_env\python.exe -m pip install --pre --index-url https://nightly.repo.amd.com/rocm/whl-next/ -r .\tested-rocm-packages.txt
if ($LASTEXITCODE -ne 0) { throw 'The tested package installation failed. Check the error above before continuing.' }
.\python_env\python.exe -m pip install triton-windows==3.7.0.post26
if ($LASTEXITCODE -ne 0) { throw 'Triton installation failed.' }
.\python_env\Scripts\rocm-sdk.exe init
if ($LASTEXITCODE -ne 0) { throw 'ROCm SDK initialization failed.' }
```

The pinned Windows wheels were available from AMD's index when this guide was published on October 1, 2026. If AMD removes these nightly versions, a latest-version install does not reproduce this runtime. Use the experimental source builders for a different environment or wait for a tested compatible release.

These commands match the recorded runtime package versions. A complete fresh installation with these instructions has not been retested; other dependencies, drivers, models and settings can also affect behavior.

## 3. Check the runtime before adding the nodes

From the same folder, run:

```powershell
.\python_env\python.exe -c "import sys, torch, importlib.metadata as m; print('Python:', sys.version.split()[0]); print('Torch:', torch.__version__); print('HIP:', torch.version.hip); assert sys.version_info[:3] == (3,12,9), 'Expected Python 3.12.9'; assert torch.__version__ == '2.15.0a0+rocm10.2.0a20260926', 'Torch version differs'; assert torch.version.hip == '7.17.26384', 'HIP version differs'; assert torch.cuda.is_available(), 'ROCm GPU is unavailable'; gpu=torch.cuda.get_device_properties(0); arch=getattr(gpu,'gcnArchName',''); print('GPU:',gpu.name); print('Architecture:',arch); assert arch.split(':')[0] == 'gfx1201', 'Expected gfx1201'; expected={'rocm-sdk-core':'10.2.0a20260926','rocm-sdk-libraries':'10.2.0a20260926','rocm-sdk-devel':'10.2.0a20260927'}; actual={k:m.version(k) for k in expected}; print('SDK packages:',actual); assert actual == expected, 'SDK versions differ'; print('PASS: tested Python/Torch/HIP/SDK and GPU architecture match')"
if ($LASTEXITCODE -ne 0) { throw 'Runtime check failed. Resolve the reported mismatch before installing the precompiled nodes.' }
```

Expected setup:

| Component | Tested value |
| --- | --- |
| OS | Windows 11 x64 |
| GPU | RX 9070 XT / gfx1201 |
| Python | 3.12.9 |
| Torch | 2.15.0a0+rocm10.2.0a20260926 |
| HIP | 7.17.26384 |
| ROCm SDK | 10.2, package pins above |
| Triton | triton-windows 3.7.0.post26 |

Keep these runtime versions when using the fixed precompiled release. `rocm-pytorch-package-updater.bat` installs newer runtime packages; check compatibility before running it. The video covers ComfyUI ROCm generally, while these precompiled nodes are tested on the specific setup above.

## 4. Install the AMD nodes

1. Close ComfyUI.
2. On the AMD node repository's **main** branch, choose **Code → Download ZIP**.
3. Extract the node folder directly into `ComfyUI-ROCm\custom_nodes`. Its `__init__.py` must sit directly inside the node folder.
4. Move any older copy of the same node outside `custom_nodes`.
5. Follow that node's `PRECOMPILED_INSTALL.txt` for its remaining dependencies. CuMesh and O-Voxel dependencies need their supplied wheels installed with ComfyUI's Python. Blender and model weights are separate downloads where required.
6. Start ComfyUI with `comfyui-user.bat` and check that the nodes load.

For Bake Forger, the tested baking tool is **Blender 5.2 with Cycles HIP**. Build tools are only needed for source builds; see `COMFYUI_ROCM_BUILD_GUIDE.md` and the repository's **experimental-auto-arch** branch for those instructions.

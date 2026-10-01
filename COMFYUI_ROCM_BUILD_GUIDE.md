# Building WTiVo nodes with ComfyUI ROCm on Windows

These ports were built using the Python interpreter and ROCm PyTorch already used
by a working ComfyUI installation based on
[patientx-cfz/comfyui-rocm](https://github.com/patientx-cfz/comfyui-rocm).
That environment supplied Torch, the HIP runtime, the matching packaged ROCm SDK,
and ComfyUI APIs. Extra native compiler tools and CPU libraries were needed for
the extensions. Blender was installed separately for baking.

This guide records the method and gives portable command examples. The original
ports were built and tested; a fresh rebuild of the publication folders using
these commands has not been performed. The installer's current downloads can
differ from the exact tested versions below.

## Tested environment

| Component | Version or hardware |
| --- | --- |
| Operating system | Windows 11, x64 |
| GPU | AMD RX 9070 XT, gfx1201, 16 GB VRAM |
| System memory | 64 GB |
| Python | 3.12.9 |
| Torch | 2.15.0a0+rocm10.2.0a20260926 |
| HIP | 7.17.26384 |
| ROCm SDK | 10.2 |
| Triton | triton-windows 3.7.0.post26 |
| Native toolchain | Visual Studio 18 Build Tools, x64 C++ tools, Ninja |
| Bake tool | Blender 5.2, Cycles HIP |

The fixed release targets gfx1201. The separate experimental release detects a
GPU architecture or accepts an override. Neither the installer supporting a GPU
nor the builder detecting it establishes that these mesh ports work on that GPU.

## Prepare the existing installation

For a new ComfyUI installation, follow the installer's own prerequisites and
installation steps. Its README describes `python_env` and packaged ROCm components;
a separate system HIP installation is not required for its normal setup.
For an existing working installation, start with its current environment.
Do not rerun the installer or replace Torch merely to build these nodes.

Close ComfyUI before installing native modules. Open **Developer PowerShell** for
your Visual Studio C++ Build Tools, configured for x64. This supplies the MSVC
headers, linker, Windows SDK and libraries. Ordinary PowerShell alone does not
initialize that compiler environment. Add your installed Ninja directory to PATH
if the developer shell does not already provide it.

Choose your own paths. The values below are examples, not required locations:

```powershell
$ComfyRoot = 'C:\AI\ComfyUI-ROCm'
$BuildPython = Join-Path $ComfyRoot 'python_env\python.exe'
$NodeSources = 'C:\Build\amd-nodes'

if (!(Test-Path -LiteralPath $BuildPython)) { throw 'Check the ComfyUI Python path' }
& $BuildPython -c "import sys, torch; print(sys.executable); print(torch.__version__); print('HIP:', torch.version.hip); print('GPU available:', torch.cuda.is_available()); print(torch.cuda.get_device_properties(0))"
```

Use `$BuildPython` for every Python and pip command. `torch.version.hip` must be
present and GPU availability must be true. PyTorch deliberately uses `torch.cuda`
interfaces for HIP, as explained in its
[ROCm documentation](https://docs.pytorch.org/docs/stable/notes/hip.html).

Record the working package versions before installing missing build dependencies:

```powershell
& $BuildPython -m pip freeze | Set-Content '.\packages-before-build.txt'
```

## Select the matching physical SDK

The build used the real SDK payload in `_rocm_sdk_core` inside this Python's
site-packages. The development overlay had inaccessible header links on the tested
machine. Pointing to the physical core payload resolved those failures.

```powershell
$SdkRoot = (& $BuildPython -c "import importlib.util; from pathlib import Path; s=importlib.util.find_spec('_rocm_sdk_core'); assert s and s.origin, 'Physical core SDK not found'; print(Path(s.origin).parent)").Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot locate the matching SDK' }

$HipCompiler = Join-Path $SdkRoot 'lib\llvm\bin\clang-cl.exe'
if (!(Test-Path -LiteralPath $HipCompiler)) { throw 'SDK compiler missing' }

$env:ROCM_HOME = $SdkRoot
$env:HIP_PATH = $SdkRoot
$env:CXX = $HipCompiler
$env:MAX_JOBS = '2'
$env:DISTUTILS_USE_SDK = '1'
$env:MSSdk = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PATH = (Join-Path $ComfyRoot 'python_env\Scripts') + ';' + $env:PATH

Get-Command ninja
Get-Command cmake
```

If your installer version packages the SDK differently, inspect that version's
layout and resolve the matching physical SDK before continuing. Do not substitute
an unrelated ROCm version. The saved build used Torch's native extension loader,
with HIP compiler options such as `-O2`, `-std=c++20` and the GPU offload target.
Do not forward custom MSVC `/...` options into HIP compiler flags.

## Source folder layout

Put the contents of each prepared repository under `$NodeSources`:

```text
amd-nodes/
  ComfyUI-WTiVo-WatertightVoxel-AMD/
  ComfyUI-Mesh-Quad-Reconstruct-AMD/
    CuMesh-HIP/
  ComfyUI-CuMesh-Decimate-AMD/
    CuMesh-HIP/
  ComfyUI-Trellis2-Mesh-Encoder-AMD/
    HIP-runtime/
  ComfyUI-LODTailor-Bake-Forger-AMD/
```

Choose the fixed or experimental release consistently. The two CuMesh folders
contain the same backend; build and install one of them when using both nodes.
These are source repositories. Native modules and weights are excluded.

## WTiVo CPU modules

WTiVo needs CPU modules for tetrahedralization and OpenVDB processing as well as
its HIP graph solver. These modules link against CGAL, Eigen, oneTBB, OpenVDB and
their transitive dependencies. The original successful build used CGAL 6.2,
Eigen 5.0.1, oneTBB 2023.1.0 and OpenVDB 12.0.1, supplied through a separately
prepared vcpkg dependency tree. That dependency tree is not bundled here.

Prepare an x64 Windows vcpkg installation with the dependencies listed in
`vcpkg.json`, then set the paths to its toolchain and installed packages.
The example below uses an existing dependency tree, matching the original method.
Building a new dependency tree may require additional package-specific fixes;
that fresh dependency build has not been validated by this publication preparation.

Install missing build tools with this same interpreter, without replacing Torch:

```powershell
$NodeRoot = Join-Path $NodeSources 'ComfyUI-WTiVo-WatertightVoxel-AMD'
& $BuildPython -m pip install --no-deps -r (Join-Path $NodeRoot 'requirements-build.txt')

$CppDeps = 'C:\Build\vcpkg'
$CppInstalled = 'C:\Build\vcpkg_installed'
$PybindCmake = (& $BuildPython -c "import pybind11; print(pybind11.get_cmake_dir())").Trim()

cmake -S $NodeRoot -B (Join-Path $NodeRoot '.build\cpu') -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  "-DCMAKE_TOOLCHAIN_FILE=$CppDeps\scripts\buildsystems\vcpkg.cmake" `
  -DVCPKG_MANIFEST_MODE=OFF `
  "-DVCPKG_INSTALLED_DIR=$CppInstalled" `
  -DVCPKG_TARGET_TRIPLET=x64-windows `
  "-DPython3_EXECUTABLE=$BuildPython" `
  "-Dpybind11_DIR=$PybindCmake"
if ($LASTEXITCODE -ne 0) { throw 'CPU configuration failed' }

cmake --build (Join-Path $NodeRoot '.build\cpu') --config Release -j 2
if ($LASTEXITCODE -ne 0) { throw 'CPU build failed' }
```

CMake places `wtivo_core.pyd` and `wtivo_vdb.pyd` in the node's `build/` folder.
Their dependent DLLs must also be available. The runtime looks in `build/` and
the node-local `.deps/vcpkg/installed/x64-windows/bin` directory. If dependencies
were built elsewhere, copy their required release DLLs into `build/`, retaining
their licenses. Missing dependent DLLs can make a `.pyd` fail even when it exists.

## WTiVo HIP graph solver

From the same developer shell and interpreter:

```powershell
& $BuildPython (Join-Path $NodeRoot 'scripts\build_gpupr_hip.py')
if ($LASTEXITCODE -ne 0) { throw 'HIP graph build failed' }

& $BuildPython (Join-Path $NodeRoot 'scripts\verify_hip_graph.py')
if ($LASTEXITCODE -ne 0) { throw 'Graph validation failed' }
```

This produces `build/wtivo_gpupr.pyd`. The original work translated GPU runtime
calls to HIP, fixed the empty graph result arity, and returned owned Eigen vertex
data to avoid a borrowed-memory lifetime problem. The verification script checks
small graph behavior; it does not establish every production mesh succeeds.

## Shared CuMesh backend

The VisualBruno CuMesh source commit used was
`d10e54c30ddd03d11472c1431693f985501c7966`. Its HIP source, BVH/atlas components,
AMD headers and third-party licenses are bundled with Quad and Decimate.

```powershell
$QuadRoot = Join-Path $NodeSources 'ComfyUI-Mesh-Quad-Reconstruct-AMD'
Set-Location -LiteralPath $QuadRoot
& $BuildPython '.\CuMesh-HIP\build_hip.py'
if ($LASTEXITCODE -ne 0) { throw 'CuMesh HIP build failed' }

& $BuildPython -m pip install '.\CuMesh-HIP' --no-build-isolation --no-deps
if ($LASTEXITCODE -ne 0) { throw 'CuMesh installation failed' }
& $BuildPython -c "import cumesh; print(cumesh.__file__)"
```

The backend builds `_C`, `_cubvh` and `_xatlas`, then installs `cumesh` into the
same ComfyUI environment. `--no-build-isolation --no-deps` keeps backend packaging
from installing a different Torch. Ensure its small runtime dependency `tqdm`
and the node's PyMeshLab dependency are present separately. The tested PyMeshLab
version was 2025.7.post1; trimesh was 4.10.1.

The port also fixed a large-array HIP upload truncation: contiguous arrays use
flat copies and padded arrays use bounded row chunks. This was verified by exact
upload equality before the large Quad reconstruction tests.

## Trellis2 encoder and O Voxel

```powershell
$EncoderRoot = Join-Path $NodeSources 'ComfyUI-Trellis2-Mesh-Encoder-AMD'
Set-Location -LiteralPath $EncoderRoot
& $BuildPython -m pip install --no-deps -r '.\requirements.txt'
& $BuildPython '.\HIP-runtime\build_hip.py'
if ($LASTEXITCODE -ne 0) { throw 'O-Voxel HIP build failed' }
& $BuildPython '.\HIP-runtime\install_runtime.py'
if ($LASTEXITCODE -ne 0) { throw 'Encoder runtime installation failed' }
```

The runtime installer refuses to overwrite an existing `trellis2` or `o_voxel`
package. Back up and deliberately resolve existing packages before installing.
The original installation likewise copied the runtime into the active interpreter's
site-packages. This focused encoder runtime uses ComfyUI's Torch sparse convolution
implementation, lazy optional imports, strict encoder weight loading and ComfyUI's
SparseTensor for VAE subdivision decoding. Full image generation was not ported.

Obtain the matching `shape_enc_next_dc_f16c32_fp16.json` and
`shape_enc_next_dc_f16c32_fp16.safetensors` from the official
[Microsoft checkpoint repository](https://huggingface.co/microsoft/TRELLIS.2-4B/tree/main/ckpts).
Place both in `ComfyUI/models/Trellis2/encoders`. Use the Trellis2 shape VAE in
the workflow. Weights are separate downloads and are not in these source packages.
ComfyUI must supply `comfy.ldm.trellis2.vae` and `comfy.ldm.trellis2.flexgemm`.

## Bake Forger

Bake Forger did not need a native Torch extension build. Blender 5.2 was installed
separately, and its Cycles HIP devices performed the bake. The port discovers
Blender when its path field is blank, `blender` or `blender.exe`, and logs the
selected devices. An explicit Blender path also works.

Install the node's listed Python dependencies into the existing ComfyUI environment
as needed. Select HIP in the node and start with a small bake. Its existing
`output/latest` cleanup behavior means validation should use a separate output
folder. The successful test used six 64x64 maps, one sample and hybrid CPU disabled.

## Experimental GPU selection

Only the experimental release adds these options. Examples:

```powershell
& $BuildPython (Join-Path $QuadRoot 'CuMesh-HIP\build_hip.py') --detect-only
& $BuildPython (Join-Path $QuadRoot 'CuMesh-HIP\build_hip.py') --device 0
& $BuildPython (Join-Path $QuadRoot 'CuMesh-HIP\build_hip.py') --arch gfx1100 --device 0
```

The same options work with WTiVo's graph builder and the O-Voxel builder.
`HIP_ARCH` is the shared environment override. Detection-only runs compile and
install nothing. An override cannot add support missing from Torch, drivers or
the SDK. JIT builders load the compiled extension locally, so an incompatible
override can fail during loading. Builds replace the output modules; they do not
create a multi-GPU binary bundle. Actual inference on other architectures remains
unvalidated.

## Install nodes and validate the workflow

Copy the completed node folders into ComfyUI `custom_nodes`, keeping each node's
`__init__.py` directly inside its folder. Move previous versions outside
`custom_nodes` to avoid duplicate node registrations. Launch ComfyUI with its
existing ROCm launcher. Native modules were built against that exact environment;
Torch/SDK/Python changes may require rebuilding.

The original verification progressed from native imports and small graph/mesh
tests to installed node registration and actual node execution:

| Component | Completed validation |
| --- | --- |
| Eight workflow packs | Imports, registration and exposed inputs |
| WTiVo | Small graph/cube tests and an actual 2048 workflow, about 25 million input points, 38,677,180 output faces, watertight |
| Quad | Actual node at 2048, band 1, floaters/inner-face filtering enabled; 41,649,228 faces, watertight and consistent winding |
| Decimate | Actual node reduced a sphere from 320 to 152 faces |
| Encoder | Official weights and ComfyUI VAE, cube tests at 256/1024/2048, finite 32-channel latents and four subdivision stages |
| Bake Forger | Six-map HIP bake and GLB export at 64x64, one sample |
| Experimental selectors | 12 tests, four actual detection-only builder checks, explicit override selection; no new native rebuild |

Start a user's own workflow with a real mesh filename and modest settings.
An import or cube test does not establish arbitrary complex mesh quality or memory
use. Keep the original environment and build records so failures can be attributed
to the node, source change, input or dependency version.

## Common build failures

| Symptom | What to check |
| --- | --- |
| Missing HIP or no GPU | Confirm the ComfyUI interpreter, ROCm Torch and driver are working before building |
| SDK headers missing | Resolve the matching physical SDK payload; avoid the failed development-overlay links |
| Ninja/MSVC/Windows headers missing | Use the x64 developer shell and put Ninja on PATH |
| HIP compiler rejects `/...` arguments | Avoid custom MSVC flags forwarded into HIP compilation |
| Native module exists but cannot import | Match Python/Torch/SDK and make dependent DLLs available |
| Existing Trellis runtime refused | Resolve the existing installation deliberately; the installer protects it from replacement |
| Encoder imports fail outside ComfyUI | ComfyUI APIs require its root on Python's search path; validate through the running application |

This guide is based on the saved successful build records and installed-node
validation, with portable paths substituted for the original machine locations.

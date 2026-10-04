from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys


NODE_DIR = Path(__file__).resolve().parent


def _run(command, env=None):
    command = [str(item) for item in command]
    if env is not None:
        executable = shutil.which(command[0], path=env.get("PATH"))
        if executable:
            command[0] = executable
    print("[Installer]", subprocess.list2cmdline(command), flush=True)
    subprocess.check_call(command, cwd=NODE_DIR, env=env)




def _install(env):
    _run([sys.executable, "-m", "pip", "install", "--no-build-isolation", "-r", "requirements.txt"], env)
    print("Bake Forger uses Blender Cycles HIP; there is no native extension to compile.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check prerequisites without compiling or installing.")

    args = parser.parse_args()
    import torch
    if not torch.version.hip:
        raise RuntimeError("Use the ROCm PyTorch environment that runs ComfyUI.")
    if not torch.cuda.is_available():
        raise RuntimeError("The ROCm GPU is unavailable in this PyTorch environment.")
    print("[Installer] Python:", sys.executable)
    print("[Installer] PyTorch:", torch.__version__, "HIP:", torch.version.hip)
    env = os.environ.copy()
    if args.check:
        print("[Installer] Prerequisites checked; no modules were compiled or installed.")
        return 0
    _install(env)
    print("[Installer] Installation completed. If installing a node group, wait for all installers before restarting ComfyUI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

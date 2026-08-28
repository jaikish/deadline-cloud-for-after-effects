# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""ERR-4 crash-prevention test: KMP_DUPLICATE_LIB_OK=TRUE actually suppresses the
Intel OpenMP "OMP: Error #15" abort.

The pure-function / env-plumbing tests in test_call_aerender.py prove
build_render_env() sets the variable and that the aerender child receives it, but
not that the variable prevents the crash it exists for. This test loads TWO copies
of the Intel OpenMP runtime (libiomp5md.dll -- AE's own shipped binary) into one
subprocess, which is the exact "multiple copies of the OpenMP runtime linked into
the program" condition an AE plugin (Trapcode / Element 3D) creates. It asserts:

  * with a stock environment (no KMP_DUPLICATE_LIB_OK) the process aborts with OMP
    Error #15, and
  * launched via call_aerender.build_render_env() it runs to completion.

Skipped unless AE's libiomp5md.dll is present (Windows workers / dev boxes with AE
installed), so it is a no-op on macOS and CI hosts without AE.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "dist"
    / "DeadlineCloudSubmitter_Assets"
    / "JobTemplate"
    / "scripts"
)
_SPEC = importlib.util.spec_from_file_location(
    "call_aerender", _SCRIPTS_DIR / "call_aerender.py"
)
call_aerender = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(call_aerender)

# AE's own OpenMP runtime. Candidate paths across installed AE versions.
_AE_OMP_CANDIDATES = [
    r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\libiomp5md.dll",
    r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\libiomp5md.dll",
]
_AE_OMP = next((p for p in _AE_OMP_CANDIDATES if os.path.exists(p)), None)

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or _AE_OMP is None,
    reason="needs a Windows host with AE's libiomp5md.dll present",
)

# Minimal program: load two copies of the given OpenMP runtime and force init.
# The second copy triggers OMP Error #15 unless KMP_DUPLICATE_LIB_OK is set.
_REPRO = """
import ctypes, os, shutil, sys, tempfile
src = os.environ["OMP_SRC"]
d = tempfile.mkdtemp()
a = os.path.join(d, "omp_a.dll"); b = os.path.join(d, "omp_b.dll")
shutil.copyfile(src, a); shutil.copyfile(src, b)
for p in (a, b):
    lib = ctypes.CDLL(p)
    lib.omp_get_max_threads.restype = ctypes.c_int
    lib.omp_get_max_threads()
print("BOTH_LOADED_OK", flush=True)
"""


def _run(env):
    env = dict(env)
    env["OMP_SRC"] = _AE_OMP
    return subprocess.run(
        [sys.executable, "-c", _REPRO],
        env=env,
        capture_output=True,
        text=True,
    )


def _stock_env():
    return {k: v for k, v in os.environ.items() if k != "KMP_DUPLICATE_LIB_OK"}


def test_stock_env_aborts_with_omp_error_15():
    result = _run(_stock_env())
    assert result.returncode != 0
    assert "Error #15" in (result.stdout + result.stderr)
    assert "BOTH_LOADED_OK" not in result.stdout


def test_build_render_env_prevents_the_crash():
    result = _run(call_aerender.build_render_env(base_env=_stock_env()))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BOTH_LOADED_OK" in result.stdout


# A stand-in aerender that recreates the plugin duplicate-OpenMP condition and, if
# it survives, behaves like a healthy render (frame line + writes -output).
_RENDER_CHILD = """
import ctypes, os, shutil, sys, tempfile
src = os.environ["OMP_SRC"]
d = tempfile.mkdtemp()
for name in ("a.dll", "b.dll"):
    p = os.path.join(d, name); shutil.copyfile(src, p)
    lib = ctypes.CDLL(p); lib.omp_get_max_threads.restype = ctypes.c_int
    lib.omp_get_max_threads()          # 2nd copy aborts here unless KMP is set
s = 0
argv = sys.argv[1:]
for i, a in enumerate(argv):
    if a == "-s" and i + 1 < len(argv): s = int(argv[i + 1])
print("PROGRESS:  0:00:00:%02d (%d): 0 Seconds" % (s, s), flush=True)
for i, a in enumerate(argv):
    if a == "-output" and i + 1 < len(argv):
        o = argv[i + 1].strip().strip('"').replace("[#####]", "%05d" % s)
        os.makedirs(os.path.dirname(o) or ".", exist_ok=True)
        open(o, "wb").write(b"x")
"""


def test_run_survives_duplicate_openmp_end_to_end(tmp_path, monkeypatch):
    """Full run() path: with the fix, a render whose aerender hits the
    duplicate-OpenMP condition completes (rc 0) instead of aborting. The stock
    submitter (no build_render_env) fails this same scenario with OMP Error #15 --
    see specs/progress/omp_repro/."""
    child = tmp_path / "omp_render_child.py"
    child.write_text(_RENDER_CHILD, encoding="utf-8")
    outpath = str(tmp_path / "o_[#####].png")

    monkeypatch.setenv("OMP_SRC", _AE_OMP)
    monkeypatch.setenv("AERENDER_EXECUTABLE", sys.executable)
    monkeypatch.delenv("KMP_DUPLICATE_LIB_OK", raising=False)  # clean worker env
    orig = call_aerender.build_render_args
    monkeypatch.setattr(
        call_aerender, "build_render_args", lambda a, s, e: [str(child)] + orig(a, s, e)
    )

    rc = call_aerender.run(["proj.aep", "0", outpath, "0-0"])
    assert rc == 0

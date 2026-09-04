#!/usr/bin/env python3
"""Resolve the Mac Qwen/MLX runtime. Fail-closed. Never fall back to Kokoro."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from tools.tts.metal_preflight import default_metal_device_available
    from tools.tts.voice_registry import VoiceRegistry
except ImportError:
    from metal_preflight import default_metal_device_available
    from voice_registry import VoiceRegistry


TTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TTS_ROOT.parents[1]
PINNED_MLX_AUDIO = "0.4.5"
MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit"
MODEL_REVISION = "50f45ef0047cde7e84c2ef04326acb8ada2436a7"
DEMO_VOICE_ID = "CV007"

KOKORO_BAN = "不要改用 Kokoro。v1 真配音只走 Apple Silicon 上的 Qwen3-TTS + MLX。"


class SetupError(RuntimeError):
    """User-actionable Chinese setup failure. Not a stack-trace dump."""


@dataclass
class Check:
    name: str
    status: str
    detail: str


@dataclass
class SetupReport:
    ok: bool
    voice_id: str
    checks: list[Check] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    qwen_python: str | None = None
    qwen_model: str | None = None
    reference: Path | None = None


@dataclass(frozen=True)
class ReadyRuntime:
    voice_id: str
    qwen_python: str
    qwen_model: str
    reference: Path
    reference_text: str
    sample_rate_hz: int
    language: str


def is_apple_silicon(
    *,
    platform_name: str | None = None,
    machine_name: str | None = None,
) -> bool:
    system = platform_name if platform_name is not None else sys.platform
    machine = machine_name if machine_name is not None else platform.machine()
    return system == "darwin" and machine in {"arm64", "aarch64"}


def resolve_qwen_python(registry: VoiceRegistry | None = None) -> str | None:
    value = registry or VoiceRegistry.load()
    env_name = value.config["runtime"]["qwen_python_env"]
    configured = os.environ.get(env_name)
    if configured:
        return configured
    for candidate in value.config["runtime"]["qwen_python_candidates"]:
        path = TTS_ROOT / candidate
        if path.is_file():
            return str(path)
    return None


def resolve_qwen_model(registry: VoiceRegistry | None = None) -> str | None:
    value = registry or VoiceRegistry.load()
    for env_name in value.config["runtime"]["qwen_base_model_envs"]:
        configured = os.environ.get(env_name)
        if configured:
            return configured
    for candidate in value.config["runtime"]["qwen_base_model_candidates"]:
        path = TTS_ROOT / candidate
        if path.exists():
            return str(path)
    return None


def model_tree_looks_valid(path: Path) -> bool:
    if not path.is_dir():
        return False
    if (path / "config.json").is_file():
        return True
    return any(path.glob("*.safetensors")) or any(path.glob("*.npz"))


def mlx_audio_version(python_bin: str, *, timeout: float = 30.0) -> str | None:
    script = (
        "import importlib.metadata as m\n"
        "print(m.version('mlx-audio'))\n"
    )
    try:
        completed = subprocess.run(
            [python_bin, "-c", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    version = completed.stdout.strip().splitlines()
    return version[-1].strip() if version else None


def _python_executable(path: str) -> bool:
    candidate = Path(path).expanduser()
    return candidate.is_file() and os.access(candidate, os.X_OK)


def inspect_setup(
    voice_id: str | None = None,
    *,
    registry: VoiceRegistry | None = None,
    platform_name: str | None = None,
    machine_name: str | None = None,
    metal_checker=None,
    check_mlx_import: bool = True,
) -> SetupReport:
    value = registry or VoiceRegistry.load()
    target_id = voice_id or DEMO_VOICE_ID
    report = SetupReport(ok=True, voice_id=target_id)
    qwen = value.config.get("qwen_base", {})
    pinned = str(qwen.get("mlx_audio_version") or PINNED_MLX_AUDIO)

    apple = is_apple_silicon(platform_name=platform_name, machine_name=machine_name)
    system = platform_name if platform_name is not None else sys.platform
    machine = machine_name if machine_name is not None else platform.machine()
    if apple:
        report.checks.append(Check("系统", "PASS", "Apple Silicon Mac"))
    else:
        report.ok = False
        detail = f"当前是 {system}/{machine}，真配音需要 Apple Silicon（M 系列）Mac。"
        report.checks.append(Check("系统", "FAIL", detail))
        report.errors.append(f"{detail} {KOKORO_BAN}")
        report.next_steps.append("换一台 M 系列 Mac，按 docs/mac-setup.md 从 bootstrap 做起。")

    metal_ok = False
    if apple:
        checker = metal_checker or default_metal_device_available
        metal_ok = bool(checker())
        if metal_ok:
            report.checks.append(Check("Metal", "PASS", "默认 Metal 设备可用"))
        else:
            report.ok = False
            detail = "没有默认 Metal 设备。请在本机终端重跑，不要用远程 Linux / 无 GPU 的会话。"
            report.checks.append(Check("Metal", "FAIL", detail))
            report.errors.append(f"{detail} {KOKORO_BAN}")
            report.next_steps.append("在 Mac 本机终端执行：python3 tools/tts/metal_preflight.py")
    else:
        report.checks.append(Check("Metal", "SKIP", "非 Darwin，已跳过 Metal 探测"))

    python_bin = resolve_qwen_python(value)
    env_python = value.config["runtime"]["qwen_python_env"]
    if not python_bin:
        report.ok = False
        detail = f"{env_python} 未设置，也没有 tools/tts/qwen.venv/bin/python。"
        report.checks.append(Check(env_python, "UNSET", detail))
        report.errors.append(f"{detail} {KOKORO_BAN}")
        report.next_steps.append("在 Mac 上跑：bash tools/tts/bootstrap_mac.sh")
        report.next_steps.append(f"然后：source tools/tts/runtime/env.sh   # 或手动 export {env_python}")
    elif not _python_executable(python_bin):
        report.ok = False
        detail = f"{env_python} 指向的解释器不存在或不可执行：{python_bin}"
        report.checks.append(Check(env_python, "FAIL", detail))
        report.errors.append(f"{detail} 请重跑 bash tools/tts/bootstrap_mac.sh")
        report.next_steps.append("bash tools/tts/bootstrap_mac.sh")
    else:
        report.qwen_python = python_bin
        report.checks.append(Check(env_python, "PASS", python_bin))
        if check_mlx_import:
            version = mlx_audio_version(python_bin)
            if version is None:
                report.ok = False
                detail = f"这个解释器 import 不了 mlx-audio {pinned}。"
                report.checks.append(Check("mlx-audio", "FAIL", detail))
                report.errors.append(
                    f"{detail} 请用 bootstrap 建的 qwen.venv，不要用系统 Python。{KOKORO_BAN}"
                )
                report.next_steps.append("bash tools/tts/bootstrap_mac.sh")
            elif not version.startswith(pinned):
                report.ok = False
                detail = f"钉的是 mlx-audio=={pinned}，现在是 {version}。"
                report.checks.append(Check("mlx-audio", "FAIL", detail))
                report.errors.append(f"{detail} 请重装钉死版本，不要随手 pip install -U。")
                report.next_steps.append(
                    f"{python_bin} -m pip install 'mlx-audio=={pinned}'"
                )
            else:
                report.checks.append(Check("mlx-audio", "PASS", version))

    model = resolve_qwen_model(value)
    env_model = value.config["runtime"]["qwen_base_model_envs"][0]
    if not model:
        report.ok = False
        detail = f"{env_model} 未设置。权重不随仓库分发。"
        report.checks.append(Check(env_model, "UNSET", detail))
        report.errors.append(
            f"{detail} 请从 Hugging Face 合法下载 {MODEL_ID}（revision {MODEL_REVISION[:12]}…）。"
            f" {KOKORO_BAN}"
        )
        report.next_steps.append("打开 docs/mac-setup.md 的「下载权重」一节，复制 huggingface-cli 命令。")
        report.next_steps.append(f"export {env_model}=/你的/本地/Qwen3-TTS-12Hz-0.6B-Base-8bit")
    else:
        model_path = Path(model).expanduser()
        if not model_path.exists():
            report.ok = False
            detail = f"{env_model} 路径不存在：{model_path}"
            report.checks.append(Check(env_model, "FAIL", detail))
            report.errors.append(f"{detail} 权重不随仓库分发，需要你自己放到这个目录。")
            report.next_steps.append("核对下载目录后重新 export，再跑 python3 tools/tts/setup_check.py")
        elif not model_tree_looks_valid(model_path):
            report.ok = False
            detail = f"{model_path} 不像 Qwen3-TTS 模型树（缺少 config.json / safetensors）。"
            report.checks.append(Check(env_model, "FAIL", detail))
            report.errors.append(
                f"{detail} 不要指向空文件夹。合法来源：https://huggingface.co/{MODEL_ID}"
            )
            report.next_steps.append("按 docs/mac-setup.md 重新下载到一个非空目录。")
        else:
            report.qwen_model = str(model_path)
            report.checks.append(Check(env_model, "PASS", str(model_path)))

    voice = value.by_id(target_id)
    if voice is None:
        report.ok = False
        detail = f"登记里没有 {target_id}。"
        report.checks.append(Check("参考 WAV", "FAIL", detail))
        report.errors.append(detail)
    else:
        reference = value.reference_path_for(voice)
        if reference.is_file():
            report.reference = reference
            report.checks.append(Check("参考 WAV", "PASS", str(reference)))
        else:
            report.ok = False
            local = value.local_reference_path_for(voice)
            detail = f"{target_id} 还没有参考 WAV（期望 {local.as_posix()}）。"
            report.checks.append(Check("参考 WAV", "FAIL", detail))
            report.errors.append(
                f"{detail} 请在安静房间自录约 10 秒单声道 WAV，再安装到教学声槽。"
            )
            report.next_steps.append(
                "python3 tools/tts/install_reference.py ~/Desktop/reference.wav"
                f" --voice {target_id}"
            )
            report.next_steps.append("录音说明：tools/tts/voices/local/README.md")

    if not report.ok and KOKORO_BAN not in " ".join(report.errors):
        report.errors.append(KOKORO_BAN)
    if not report.ok:
        _dedupe(report.next_steps)
        if "python3 tools/tts/setup_check.py" not in report.next_steps:
            report.next_steps.append("齐了之后再跑：python3 tools/tts/setup_check.py")
    return report


def require_generation_ready(
    voice_id: str | None = None,
    **inspect_kwargs,
) -> ReadyRuntime:
    registry = inspect_kwargs.pop("registry", None) or VoiceRegistry.load()
    report = inspect_setup(voice_id, registry=registry, **inspect_kwargs)
    if not report.ok or not report.qwen_python or not report.qwen_model or report.reference is None:
        lines = ["TTS SETUP: FAIL"]
        lines.extend(f"- {error}" for error in report.errors)
        if report.next_steps:
            lines.append("下一步：")
            lines.extend(f"  {step}" for step in report.next_steps)
        raise SetupError("\n".join(lines))
    voice = registry.by_id(report.voice_id)
    if voice is None:
        raise SetupError(f"TTS SETUP: FAIL — 登记里没有 {report.voice_id}")
    engine = str(voice.get("engine") or "")
    if "kokoro" in engine.lower() or str(report.voice_id).startswith("kokoro:"):
        raise SetupError(f"TTS SETUP: FAIL — {KOKORO_BAN}")
    qwen = registry.config.get("qwen_base", {})
    return ReadyRuntime(
        voice_id=report.voice_id,
        qwen_python=report.qwen_python,
        qwen_model=report.qwen_model,
        reference=report.reference,
        reference_text=registry.reference_text_for(voice),
        sample_rate_hz=int(qwen.get("sample_rate_hz") or 24000),
        language=str(qwen.get("language") or "Auto"),
    )


def format_report(report: SetupReport) -> str:
    lines = [f"TTS 安装检查  voice={report.voice_id}"]
    for check in report.checks:
        lines.append(f"- {check.name}: {check.status}  {check.detail}")
    if report.ok:
        lines.append("TTS SETUP: PASS")
        lines.append("可以跑：python3 tools/cli.py smoke-narrate")
        return "\n".join(lines)
    lines.append("TTS SETUP: FAIL")
    for error in report.errors:
        lines.append(f"- {error}")
    if report.next_steps:
        lines.append("下一步：")
        for step in report.next_steps:
            lines.append(f"  {step}")
    which = shutil.which("ffmpeg")
    if which is None:
        lines.append("提示：本机还没有 ffmpeg 的话，Mac 上先 brew install ffmpeg。")
    return "\n".join(lines)


def _dedupe(values: list[str]) -> None:
    seen: set[str] = set()
    kept: list[str] = []
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        kept.append(item)
    values[:] = kept

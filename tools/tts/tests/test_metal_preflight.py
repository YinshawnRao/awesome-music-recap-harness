from __future__ import annotations

from tools.tts.metal_preflight import default_metal_device_available


def test_linux_has_no_metal() -> None:
    assert default_metal_device_available(platform_name="linux") is False

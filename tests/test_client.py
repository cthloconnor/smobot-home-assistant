"""Regression tests for Smobot payload normalization."""

from datetime import timedelta
import importlib.util
from pathlib import Path
import sys
import types
import unittest


def _load_client_module():
    """Load the dependency-light client module without importing Home Assistant."""
    if "aiohttp" not in sys.modules:
        aiohttp = types.ModuleType("aiohttp")
        aiohttp.ClientError = type("ClientError", (Exception,), {})
        aiohttp.ClientSession = object
        sys.modules["aiohttp"] = aiohttp

    client_path = (
        Path(__file__).parents[1] / "custom_components" / "smobot" / "client.py"
    )
    spec = importlib.util.spec_from_file_location(
        "smobot_client_under_test", client_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {client_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


client = _load_client_module()


def _payload(**overrides):
    payload = {
        "d": 999,
        "dpr": 999,
        "ds": 0,
        "err": 999,
        "fd1": 999,
        "fd2": 999,
        "flg": 0,
        "grl": 999,
        "i": 999,
        "kd": 100,
        "ki": 50,
        "kp": 110,
        "ld": 1,
        "p": 999,
        "set": 170,
        "sot": 0,
        "time": "00:00:00",
    }
    payload.update(overrides)
    return payload


class SmobotStatusTests(unittest.TestCase):
    """Verify raw values are normalized without changing the payload."""

    def test_sample_payload_normalizes_live_value_sentinels(self):
        status = client.SmobotStatus.from_api(_payload())

        self.assertIsNone(status.grill_temperature_value)
        self.assertIsNone(status.food_probe_1)
        self.assertIsNone(status.food_probe_2)
        self.assertIsNone(status.damper_state_value)
        self.assertIsNone(status.damper_mode_label)
        self.assertIsNone(status.proportional_value)
        self.assertIsNone(status.integral_value)
        self.assertIsNone(status.error_value)
        self.assertFalse(status.has_error)
        self.assertFalse(status.is_active)
        self.assertEqual("starting", status.operating_state)
        self.assertEqual("no_probes", status.probe_status)
        self.assertEqual(999, status.raw_payload["grl"])

    def test_valid_control_values_remain_available(self):
        status = client.SmobotStatus.from_api(
            _payload(
                d=0,
                dpr=52,
                fd1=203,
                grl=229,
                i=12,
                ld=0,
                p=34,
                set=250,
                time="01:02:03",
            )
        )

        self.assertEqual(229, status.grill_temperature_value)
        self.assertEqual(203, status.food_probe_1)
        self.assertEqual(52, status.damper_state_value)
        self.assertEqual("auto", status.damper_mode_label)
        self.assertEqual(34, status.proportional_value)
        self.assertEqual(12, status.integral_value)
        self.assertTrue(status.is_active)
        self.assertEqual("active", status.operating_state)
        self.assertFalse(status.lid_open)
        self.assertEqual("01:02:03", status.cook_time)

    def test_string_zero_lid_flag_is_false(self):
        status = client.SmobotStatus.from_api(_payload(ld="0"))

        self.assertFalse(status.lid_open)

    def test_pid_constant_sentinels_are_not_exposed_as_measurements(self):
        status = client.SmobotStatus.from_api(_payload(kp=999, ki=999, kd=999))

        self.assertIsNone(status.kp_value)
        self.assertIsNone(status.ki_value)
        self.assertIsNone(status.kd_value)


class FormatElapsedTimeTests(unittest.TestCase):
    """Verify the local timer's stable display format."""

    def test_formats_elapsed_time(self):
        self.assertEqual(
            "25:01:02",
            client.format_elapsed_time(timedelta(hours=25, minutes=1, seconds=2)),
        )

    def test_clamps_negative_elapsed_time(self):
        self.assertEqual(
            "00:00:00",
            client.format_elapsed_time(timedelta(seconds=-1)),
        )


if __name__ == "__main__":
    unittest.main()

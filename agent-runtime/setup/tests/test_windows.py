"""Metadata parsing and authority boundary tests, with no live Host mutation."""
import json
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_setup.windows import PINNED_IMAGE, WindowsAdapter, normalize_inventory, wsl_app_version, wsl_supported


class WindowsProbeTests(unittest.TestCase):
    def test_python_final_version_without_signature_not_verified(self):
        with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.shutil.which", return_value="powershell.exe"), patch("agent_setup.windows.documents_known_folder", return_value=None):
            adapter = WindowsAdapter(runner=lambda *a, **k: SimpleNamespace(returncode=0, stdout=json.dumps({"status": "NotSigned", "psf_signer": False})))
            self.assertFalse(adapter.probe()["python_verified"])
            self.assertEqual(adapter.probe()["python_signature"]["status"], "NotSigned")

    def test_python_verified_requires_psf_authenticode_and_final_314(self):
        class Version:
            releaselevel = "final"
            def __getitem__(self, key):
                return (3, 14)
        for status, psf, expected in [("Valid", True, True), ("Valid", False, False), ("HashMismatch", True, False)]:
            with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.sys.version_info", Version()), patch("agent_setup.windows.shutil.which", return_value="powershell.exe"), patch("agent_setup.windows.documents_known_folder", return_value=None):
                calls = []
                def run(argv, **kwargs):
                    calls.append((argv, kwargs))
                    return SimpleNamespace(returncode=0, stdout=json.dumps({"status": status, "psf_signer": psf}))
                probe = WindowsAdapter(runner=run).probe()
                self.assertEqual(probe["python_verified"], expected)
                request = json.loads(next(kwargs['input'] for _,kwargs in calls if kwargs.get('input')))
                self.assertEqual(request["path"], getattr(__import__("sys"), "_base_executable", __import__("sys").executable))
                self.assertNotIn(request["path"], calls[0][0][-1])

    def test_application_version_is_not_kernel(self):
        self.assertIsNone(wsl_app_version("Kernel version: 6.18.0\nWSL2: 2"))
        self.assertFalse(wsl_supported(wsl_app_version("WSL version: 2.6.0.0")))
        self.assertTrue(wsl_supported(wsl_app_version("WSL 版本： 3.0.0.0\n内核版本: 6.18.0")))
        self.assertEqual(wsl_app_version("\x00W\x00S\x00L\x00 version: 3.0.1.0"), "3.0.1.0")
        self.assertFalse(wsl_supported("3.0"))

    def test_inventory_whitelists_metadata(self):
        raw = {"volumes": [{"mount": "Q:\\", "fs": "NTFS", "capacity_bytes": 1000,
                            "free_bytes": 30, "device_id": "disk-0", "media_type": "SSD",
                            "bus_type": "NVMe", "serial": "NOT_FOR_OUTPUT", "token": "secret"}],
               "wsl_version_text": "WSL version: 3.0.0.0", "wslc_state": "PASS", "wslc_active_count": 2,
               "stderr": "secret", "user": "human"}
        result = normalize_inventory(raw)
        self.assertEqual(result["volumes"][0]["free_bytes"], 30)
        self.assertEqual(result["wslc_capability"]["state"], "PASS")
        self.assertNotIn("secret", json.dumps(result))
        self.assertNotIn("serial", json.dumps(result))
        self.assertEqual(result["active_workloads"][0]["count"], 2)

    def test_permission_failure_is_unknown(self):
        result = normalize_inventory({"wslc_state": "permission denied with secret"})
        self.assertEqual(result["wslc_capability"]["state"], "UNKNOWN")
        self.assertNotIn("secret", json.dumps(result))

    def test_invalid_volume_metadata_is_not_trusted(self):
        result = normalize_inventory({"volumes": [{"mount": "../x"},
                                                    {"mount": "Z:\\", "capacity_bytes": True, "free_bytes": -3}]})
        self.assertEqual(len(result["volumes"]), 1)
        self.assertIsNone(result["volumes"][0]["capacity_bytes"])
        self.assertIsNone(result["volumes"][0]["free_bytes"])

    def test_other_platform_no_commands(self):
        with patch("agent_setup.windows.sys.platform", "linux"):
            adapter = WindowsAdapter(runner=lambda *a, **k: self.fail("Must not call a command"))
            self.assertFalse(adapter.can_apply)
            self.assertEqual(adapter.probe()["wslc_capability"]["state"], "UNKNOWN")

    def test_pull_needs_authority_before_command(self):
        with patch("agent_setup.windows.sys.platform", "win32"):
            adapter = WindowsAdapter(runner=lambda *a, **k: self.fail("Must not pull"))
            self.assertEqual(adapter.pull_image(PINNED_IMAGE)["state"], "NOT_AUTHORIZED")
            self.assertEqual(adapter.pull_image("other/image:latest")["state"], "BLOCKED")

    def test_pull_exact_manifest_readback(self):
        calls = []
        config = "sha256:" + "a" * 64
        def run(argv, **kwargs):
            calls.append(argv)
            return SimpleNamespace(returncode=0, stdout=json.dumps([{"Id": config, "RepoDigests": [PINNED_IMAGE]}]))
        with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.shutil.which", return_value="wslc.exe"):
            result = WindowsAdapter(apply_authorized=True, runner=run).pull_image(PINNED_IMAGE)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["config_id"], config)
        self.assertEqual(calls[0], ["wslc.exe", "pull", PINNED_IMAGE])

    def test_wrong_manifest_and_native_error_fail_closed(self):
        for returncode, body in [(0, [{"Id": "sha256:" + "a" * 64, "RepoDigests": []}]),
                                 (1, "error token secret")]:
            with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.shutil.which", return_value="wslc.exe"):
                result = WindowsAdapter(apply_authorized=True, runner=lambda *a, **k: SimpleNamespace(returncode=returncode, stdout=json.dumps(body))).pull_image(PINNED_IMAGE)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertNotIn("secret", json.dumps(result))

    def test_start_requires_external_projection_owner(self):
        self.assertEqual(WindowsAdapter().start_runtime({}, "HOST_AGENT.md")["state"], "NOT_AUTHORIZED")

    def test_helper_never_runs_without_explicit_approval(self):
        with patch("agent_setup.windows.sys.platform", "win32"):
            adapter = WindowsAdapter(runner=lambda *a, **k: self.fail("unapproved helper execution"))
            self.assertEqual(adapter.helper_status("helper.exe")["state"], "NOT_AUTHORIZED")
            self.assertEqual(adapter.helper_status("relative.exe", approved=True)["state"], "BLOCKED")

    def test_start_scope_mismatch_before_launcher(self):
        with patch("agent_setup.windows.sys.platform", "win32"):
            adapter = WindowsAdapter(apply_authorized=True, runner=lambda *a, **k: self.fail("wrong scope"))
            with patch.object(adapter, "helper_status", return_value={"state": "READY", "repo": "other/repo", "work": "other/repo#1", "projection_directory": "Q:/protected", "server_env": "Q:/protected/server.env"}):
                self.assertEqual(adapter.start_runtime({"github": {"authorized": True, "helper_approved": True, "repo": "example/repo", "work": "example/repo#1"}}, "HOST_AGENT.md")["reason"], "HELPER_DURABLE_SCOPE_MISMATCH")

    def test_start_uses_existing_launcher_and_metadata_only(self):
        with tempfile.TemporaryDirectory() as directory:
            host = Path(directory) / "HOST_AGENT.md"
            host.write_bytes(b"context")
            digest = "sha256:" + "a" * 64
            calls = []
            def run(argv, **kwargs):
                calls.append(argv)
                return SimpleNamespace(returncode=0, stdout=json.dumps({"started": True, "name": "setup-test", "image": digest, "host_agent_sha256": hashlib.sha256(b"context").hexdigest()}))
            with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.shutil.which", return_value="wslc.exe"):
                adapter = WindowsAdapter(apply_authorized=True, runner=run)
                with patch.object(adapter, "helper_status", return_value={"state": "READY", "repo": "example/repo", "work": "example/repo#1", "projection_directory": "Q:/protected", "server_env": "Q:/protected/server.env"}):
                    result = adapter.start_runtime({"github": {"authorized": True, "helper_approved": True, "repo": "example/repo", "work": "example/repo#1"}, "runtime": {"name": "setup-test", "attempt": "Q:/attempt", "incoming": "Q:/in", "outgoing": "Q:/out"}}, host)
            self.assertEqual(result["state"], "READY")
            self.assertTrue(calls[0][1].endswith(str(Path("host/windows/launch.py"))))
            self.assertIn("--server-env", calls[0])

    def test_verifier_observes_owned_nonroot_context(self):
        with tempfile.TemporaryDirectory() as directory:
            host = Path(directory) / "HOST_AGENT.md"
            host.write_bytes(b"context")
            digest = "sha256:" + "a" * 64
            responses = iter([SimpleNamespace(returncode=0, stdout=json.dumps([{"Image": digest, "Config": {"Labels": {"agent.attempt": "setup-test"}}}])), SimpleNamespace(returncode=0, stdout=json.dumps({"uid": 1000, "hash": hashlib.sha256(b"context").hexdigest()}))])
            with patch("agent_setup.windows.sys.platform", "win32"), patch("agent_setup.windows.shutil.which", return_value="wslc.exe"):
                result = WindowsAdapter(runner=lambda *a, **k: next(responses)).verify_runtime("setup-test", host, expected_config_id=digest)
            self.assertEqual(result["state"], "PASS")
            self.assertTrue(result["nonroot"])

    def test_writeback_rejects_missing_authority_and_destination(self):
        self.assertEqual(WindowsAdapter().writeback_context({}, Path("HOST_AGENT.md"), "a" * 64)["state"], "NOT_AUTHORIZED")
        with patch("agent_setup.windows.sys.platform", "win32"):
            adapter = WindowsAdapter(apply_authorized=True, runner=lambda *a, **k: self.fail("invalid destination"))
            result = adapter.writeback_context({"github": {"authorized": True, "helper_approved": True, "repo": "example/repo", "work": "example/repo#1", "durable_destination": "https://other.example/context"}}, Path("HOST_AGENT.md"), "a" * 64)
            self.assertEqual(result["state"], "BLOCKED")

    def test_writeback_requires_exact_owner_sha_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            host = Path(directory) / "HOST_AGENT.md"
            host.write_bytes(b"context")
            sha = hashlib.sha256(b"context").hexdigest()
            destination = "https://github.com/example/repo/blob/main/host/HOST_AGENT.md"
            github = {"authorized": True, "helper_approved": True, "helper": "approved.exe", "repo": "example/repo", "work": "example/repo#1", "durable_destination": destination}
            proof = {"state": "PASS", "repo": github["repo"], "work": github["work"], "context_sha256": sha, "durable_destination": destination, "private_destination": True}
            with patch("agent_setup.windows.sys.platform", "win32"):
                adapter = WindowsAdapter(apply_authorized=True)
                with patch.object(adapter, "helper_status", return_value=proof) as helper:
                    self.assertEqual(adapter.writeback_context({"github": github}, host, sha)["state"], "PASS")
                    self.assertEqual(helper.call_args.kwargs["request"]["context_path"], str(host))
                    self.assertNotIn("context", helper.call_args.kwargs["request"])
                with patch.object(adapter, "helper_status", return_value={**proof, "context_sha256": "b" * 64}):
                    self.assertEqual(adapter.writeback_context({"github": github}, host, sha)["state"], "NOT_AUTHORIZED")
                for private_proof in (False, None, "true"):
                    with patch.object(adapter, "helper_status", return_value={**proof, "private_destination": private_proof}):
                        self.assertEqual(adapter.writeback_context({"github": github}, host, sha)["state"], "NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()

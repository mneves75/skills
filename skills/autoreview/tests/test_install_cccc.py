"""Offline installer controls; downloads and execution are mocked, no host writes."""
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
import sys
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install-cccc.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("install_cccc", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive(members):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w:gz") as package:
        for name, kind, body in members:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(body) if kind == tarfile.REGTYPE else 0
            package.addfile(member, io.BytesIO(body))
    return data.getvalue()


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_installer()
        self.temp = tempfile.TemporaryDirectory(prefix="cccc-installer-test.")
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name) / "cccc"
        self.data = archive([("cccc", tarfile.REGTYPE, b"binary")])

    def install(self, data=None, digest=None, version="cccc 1.8.0\n"):
        payload = self.data if data is None else data
        release = {"version": "1.8.0", "sha256": {
            "aarch64-apple-darwin": digest or hashlib.sha256(payload).hexdigest()}}
        with mock.patch.object(self.helper, "download", return_value=payload), \
             mock.patch.object(self.helper.subprocess, "run", return_value=
                 subprocess.CompletedProcess([], 0, version, "")):
            self.helper.install(self.destination, release, "Darwin", "arm64")

    def test_success_and_no_overwrite(self):
        self.install()
        self.assertEqual(self.destination.read_bytes(), b"binary")
        with self.assertRaises(FileExistsError):
            self.install()
        self.assertEqual(self.destination.read_bytes(), b"binary")

    def test_digest_failure_creates_nothing(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.install(digest="0" * 64)
        self.assertFalse(self.destination.exists())

    def test_archive_rejects_links_missing_duplicate_and_traversal(self):
        for members in ([('cccc', tarfile.SYMTYPE, b'')],
                        [('other', tarfile.REGTYPE, b'')],
                        [('cccc', tarfile.REGTYPE, b'a'), ('cccc', tarfile.REGTYPE, b'b')],
                        [('../cccc', tarfile.REGTYPE, b'a')]):
            with self.subTest(members=members), self.assertRaises(ValueError):
                self.install(data=archive(members))
            self.assertFalse(self.destination.exists())

    def test_version_failure_removes_only_new_binary(self):
        sentinel = self.destination.parent / "keep"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(ValueError, "version"):
            self.install(version="different tool\n")
        self.assertFalse(self.destination.exists())
        self.assertEqual(sentinel.read_text(), "keep")

    @unittest.skipIf(os.name == 'nt', "symlink privileges vary on Windows")
    def test_dangling_symlink_is_preserved(self):
        self.destination.symlink_to(self.destination.parent / "absent")
        with self.assertRaises(FileExistsError):
            self.install()
        self.assertTrue(self.destination.is_symlink())

    def test_unsupported_platform_and_missing_parent(self):
        with self.assertRaisesRegex(ValueError, "platform"):
            self.helper.install(self.destination, {}, "Windows", "AMD64")
        self.destination = self.destination.parent / "missing" / "cccc"
        with self.assertRaises(FileNotFoundError):
            self.install()

    def test_download_failure_creates_nothing(self):
        with mock.patch.object(self.helper, "download", side_effect=OSError("offline")):
            with self.assertRaises(OSError):
                self.helper.install(self.destination, self.helper.release(), "Darwin", "arm64")
        self.assertFalse(self.destination.exists())

    def test_concurrent_install_preserves_winner(self):
        def concurrent_link(source, destination):
            destination.write_text("other installer")
            raise FileExistsError("concurrent install")
        with mock.patch.object(self.helper.os, "link", side_effect=concurrent_link):
            with self.assertRaises(FileExistsError):
                self.install()
        self.assertEqual(self.destination.read_text(), "other installer")
        self.assertEqual(list(self.destination.parent.iterdir()), [self.destination])

    def test_execution_failure_leaves_no_install_or_stage(self):
        with mock.patch.object(self.helper, "download", return_value=self.data), \
             mock.patch.object(self.helper.subprocess, "run", side_effect=OSError("cannot execute")):
            release = {"version": "1.8.0", "sha256": {
                "aarch64-apple-darwin": hashlib.sha256(self.data).hexdigest()}}
            with self.assertRaises(OSError):
                self.helper.install(self.destination, release, "Darwin", "arm64")
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_binary_size_limit(self):
        with mock.patch.object(self.helper, "MAX_BINARY", 2):
            with self.assertRaisesRegex(ValueError, "bounded"):
                self.install()
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_download_guards(self):
        for url, payload, expected in (("http://insecure.example/cccc", b"ok", "HTTPS"),
                                       ("https://github.com/asset", b"large", "size limit")):
            response = mock.MagicMock()
            response.__enter__.return_value = response
            response.geturl.return_value = url
            response.read.return_value = payload
            with self.subTest(url=url), \
                 mock.patch.object(self.helper.urllib.request, "urlopen", return_value=response), \
                 mock.patch.object(self.helper, "MAX_ARCHIVE", 2):
                with self.assertRaisesRegex(ValueError, expected):
                    self.helper.download("https://github.com/asset")

    def test_interrupted_write_preserves_other_files(self):
        sentinel = self.destination.parent / "keep"
        sentinel.write_text("keep")
        real_open = Path.open
        def fail_staging(path, *args, **kwargs):
            if path.name == "cccc" and path.parent.name.startswith(".cccc-install-"):
                partial = real_open(path, *args, **kwargs)
                def interrupted_write(data):
                    partial.write(data[:1])
                    partial.flush()
                    raise OSError("disk full")
                writer = mock.MagicMock()
                writer.__enter__.return_value = writer
                writer.__exit__.side_effect = lambda *unused: partial.close()
                writer.write.side_effect = interrupted_write
                return writer
            return real_open(path, *args, **kwargs)
        with mock.patch.object(Path, "open", fail_staging):
            with self.assertRaisesRegex(OSError, "disk full"):
                self.install()
        self.assertEqual(list(self.destination.parent.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(), "keep")

    def test_cli_bad_arguments_and_existing_destination(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.destination.write_text("keep")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.destination)],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.destination.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()

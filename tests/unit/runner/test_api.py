import hashlib
import sys
import unittest
from pathlib import Path

from album.runner.api import (
    download_if_not_exists,
    download_verified,
    extract_tar,
    get_cache_path,
    in_target_environment,
)
from album.runner.core.model.solution import Solution

from tests.test_unit_common import TestUnitCommon


class TestAPI(TestUnitCommon):

    @unittest.skip("Needs to be implemented!")
    def test_get_environment_name(self):
        # ToDo: implement
        pass

    @unittest.skip("Needs to be implemented!")
    def test_get_environment_path(self):
        # ToDo: implement
        pass

    @unittest.skip("Needs to be implemented!")
    def test_get_data_path(self):
        # ToDo: implement
        pass

    @unittest.skip("Needs to be implemented!")
    def test_get_package_path(self):
        # ToDo: implement
        pass

    @unittest.skip("Needs to be implemented!")
    def test_get_app_path(self):
        # ToDo: implement
        pass

    @unittest.skip("Needs to be implemented!")
    def test_get_cache_path(self):
        # ToDo: implement
        pass

    @unittest.skipIf(sys.platform == 'win32' or sys.platform == 'cygwin',
                     "This test fails on the Windows CI with \"SSL: CERTIFICATE_VERIFY_FAILED\"")
    def test_download_if_not_exists(self):
        self.push_test_solution()

        url = "https://gitlab.com/album-app/album-solution-api/-/raw/main/.gitlab-ci.yml?inline=false"
        file_name = Path(self.tmp_dir.name).joinpath("myDownload")
        r = download_if_not_exists(url, file_name)

        self.assertTrue(Path(r).exists())
        self.assertTrue(Path(r).stat().st_size > 0)

    def _serve(self, content):
        """Write a file to download, return its url and the sha256 hash of its content."""
        served = Path(self.tmp_dir.name).joinpath("served", "model.bin")
        served.parent.mkdir(exist_ok=True)
        served.write_bytes(content)
        return served.as_uri(), "sha256:%s" % hashlib.sha256(content).hexdigest()

    def test_download_verified(self):
        self.push_test_solution()
        url, known_hash = self._serve(b"model weights")

        path = download_verified(url, "model.bin", known_hash)

        self.assertEqual(get_cache_path().joinpath("model.bin"), path)
        self.assertEqual(b"model weights", path.read_bytes())

        # in the cache: not downloaded again
        Path(self.tmp_dir.name).joinpath("served", "model.bin").unlink()
        self.assertEqual(path, download_verified(url, "model.bin", known_hash))

    def test_download_verified_other_content(self):
        self.push_test_solution()
        url, known_hash = self._serve(b"model weights")
        other_hash = "sha256:%s" % hashlib.sha256(b"other weights").hexdigest()

        # a download with another content is removed
        with self.assertRaises(ValueError) as e:
            download_verified(url, "model.bin", other_hash)

        self.assertEqual(
            "The download of %s has the sha256 hash %s, not %s."
            % (url, known_hash.split(":")[1], other_hash.split(":")[1]),
            str(e.exception),
        )
        self.assertEqual([], list(get_cache_path().iterdir()))

        # a file in the cache with another content is downloaded again
        get_cache_path().joinpath("model.bin").write_bytes(b"other weights")
        path = download_verified(url, "model.bin", known_hash)
        self.assertEqual(b"model weights", path.read_bytes())

    def test_download_verified_hash_forms(self):
        self.push_test_solution()
        url, known_hash = self._serve(b"model weights")
        digest = known_hash.split(":")[1]

        # the hex digest alone is sha256, upper case is accepted, as is another algorithm
        for index, form in enumerate(
            [digest, known_hash.upper(), "md5:%s" % hashlib.md5(b"model weights").hexdigest()]
        ):
            with self.subTest(form=form):
                path = download_verified(url, "model-%s.bin" % index, form)
                self.assertEqual(b"model weights", path.read_bytes())

        with self.assertRaises(ValueError) as e:
            download_verified(url, "model.bin", "crc32:%s" % digest)
        self.assertEqual(
            'The hash "crc32:%s" names an algorithm hashlib does not know.' % digest, str(e.exception)
        )

    def test_extract_tar(self):
        zip = self.get_resource("test_tar.tar.xz")

        extract_tar(zip, self.tmp_dir.name)

        self.assertTrue(Path(self.tmp_dir.name).joinpath("myfile").exists())
        self.assertTrue(Path(self.tmp_dir.name).joinpath("myfile").stat().st_size > 0)

    def test_in_target_environment(self):
        solution = Solution(self.get_solution_dict())
        solution._installation._environment_path = sys.executable

        self.push_test_solution(solution)

        self.assertTrue(in_target_environment())

    def test_in_target_environment_wrong_env(self):
        solution = Solution(self.get_solution_dict())
        solution._installation._environment_path = "fake_env_path"

        self.push_test_solution(solution)

        self.assertFalse(in_target_environment())

    @unittest.skip("Needs to be implemented!")
    def test_get_args(self):
        # ToDo: implement
        pass


if __name__ == '__main__':
    unittest.main()

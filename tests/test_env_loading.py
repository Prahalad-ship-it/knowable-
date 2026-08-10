import os
import tempfile
import unittest

from episteme_research import load_environment_file


class EnvLoadingTests(unittest.TestCase):
    def test_load_environment_file_reads_key_value_pairs(self):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as handle:
            handle.write("NVIDIA_API_KEY=demo-key\n")
            handle.write("NVIDIA_BASE_URL=https://example.test/v1\n")
            temp_path = handle.name

        try:
            values = load_environment_file(temp_path)
            self.assertEqual(values.get("NVIDIA_API_KEY"), "demo-key")
            self.assertEqual(values.get("NVIDIA_BASE_URL"), "https://example.test/v1")
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()

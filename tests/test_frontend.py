"""Run dependency-free JavaScript controller regressions when Node is available."""

from pathlib import Path
import shutil
import subprocess
import unittest


class FrontendControllerTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node unavailable; browser controller checks not executed")
    def test_controller_crud_filters_charts_errors_and_precision(self) -> None:
        result = subprocess.run(
            ["node", "--test", str(Path(__file__).with_name("frontend.test.js"))],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

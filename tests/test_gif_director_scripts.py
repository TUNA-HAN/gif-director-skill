import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "gif-director"
SCRIPTS = SKILL / "scripts"


def write_ppm(path: Path) -> None:
    width, height = 96, 72
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            r = int(50 + 180 * (x / (width - 1)))
            g = int(120 + 80 * (y / (height - 1)))
            b = 210 if (x + y) % 11 else 80
            pixels.extend((r, g, b))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(pixels))


class GifDirectorScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_render_validate_analyze_and_contact_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.ppm"
            output = tmp_path / "result.gif"
            report = tmp_path / "result.json"
            analysis = tmp_path / "analysis.json"
            sheet = tmp_path / "sheet.png"
            write_ppm(source)

            render = self.run_script(
                SCRIPTS / "render_gif.py",
                "--image",
                source,
                "--text",
                "퇴근하고 싶다",
                "--output",
                output,
                "--report",
                report,
                "--preset",
                "caption-pop",
                "--width",
                "160",
                "--height",
                "120",
                "--duration",
                "1.4",
            )
            self.assertEqual(render.returncode, 0, render.stderr + render.stdout)
            self.assertTrue(output.exists(), "render_gif.py should create a GIF")
            render_report = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(render_report["format"], "GIF")
            self.assertGreaterEqual(render_report["frame_count"], 8)
            self.assertEqual(render_report["width"], 160)
            self.assertEqual(render_report["height"], 120)

            validate = self.run_script(
                SCRIPTS / "validate_gif.py",
                "--input",
                output,
                "--json",
            )
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)
            validation = json.loads(validate.stdout)
            self.assertTrue(validation["ok"])
            self.assertGreaterEqual(validation["frame_count"], 8)
            self.assertGreater(validation["duration_ms"], 900)

            analyze = self.run_script(
                SCRIPTS / "analyze_reference_gif.py",
                "--input",
                output,
                "--json-output",
                analysis,
            )
            self.assertEqual(analyze.returncode, 0, analyze.stderr + analyze.stdout)
            details = json.loads(analysis.read_text(encoding="utf-8"))
            self.assertEqual(details["format"], "GIF")
            self.assertGreaterEqual(details["frame_count"], 8)
            self.assertIn("style_recipe", details)

            contact = self.run_script(
                SCRIPTS / "make_contact_sheet.py",
                "--input",
                output,
                "--output",
                sheet,
                "--columns",
                "4",
            )
            self.assertEqual(contact.returncode, 0, contact.stderr + contact.stdout)
            self.assertTrue(sheet.exists(), "make_contact_sheet.py should create a PNG")


if __name__ == "__main__":
    unittest.main()

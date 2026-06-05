import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "gif-director"
SCRIPTS = SKILL / "scripts"


def write_ppm(path: Path, blue_shift: int = 0) -> None:
    width, height = 96, 72
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            r = int(50 + 180 * (x / (width - 1)))
            g = int(120 + 80 * (y / (height - 1)))
            b = max(0, min(255, 210 - blue_shift if (x + y) % 11 else 80 + blue_shift))
            pixels.extend((r, g, b))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(pixels))


def write_sprite_sheet(path: Path) -> None:
    cell = 24
    sheet = Image.new("RGBA", (cell * 4, cell * 4), (255, 255, 255, 0))
    for index in range(16):
        x = (index % 4) * cell
        y = (index // 4) * cell
        frame = Image.new("RGBA", (cell, cell), (245, 245, 245, 255))
        color = (50 + index * 10, 80 + index * 7, 210 - index * 5, 255)
        for offset in range(4 + index % 5):
            frame.putpixel((6 + offset, 8 + index % 6), color)
            frame.putpixel((12 + index % 6, 6 + offset), color)
        sheet.alpha_composite(frame, (x, y))
    sheet.save(path)


class GifDirectorScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
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

            validate = self.run_script(SCRIPTS / "validate_gif.py", "--input", output, "--json")
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

    def test_final_service_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.ppm"
            second = tmp_path / "second.ppm"
            sprite_sheet = tmp_path / "sprite.png"
            output_dir = tmp_path / "outputs"
            write_ppm(source)
            write_ppm(second, blue_shift=30)
            write_sprite_sheet(sprite_sheet)

            for preset in ["pulse", "spin", "slide", "wiggle", "explode"]:
                output = tmp_path / f"{preset}.gif"
                render = self.run_script(
                    SCRIPTS / "render_gif.py",
                    "--image",
                    source,
                    "--text",
                    "상세페이지용 혜택 강조",
                    "--output",
                    output,
                    "--preset",
                    preset,
                    "--width",
                    "180",
                    "--height",
                    "120",
                    "--duration",
                    "1.2",
                )
                self.assertEqual(render.returncode, 0, render.stderr + render.stdout)
                validate = self.run_script(SCRIPTS / "validate_gif.py", "--input", output, "--json")
                self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)

            sprite_out = tmp_path / "sprite.gif"
            sprite_report = tmp_path / "sprite.json"
            sprite = self.run_script(
                SCRIPTS / "render_sprite_gif.py",
                "--sprite-sheet",
                sprite_sheet,
                "--output",
                sprite_out,
                "--report",
                sprite_report,
                "--cell-columns",
                "4",
                "--cell-rows",
                "4",
            )
            self.assertEqual(sprite.returncode, 0, sprite.stderr + sprite.stdout)
            self.assertEqual(json.loads(sprite_report.read_text(encoding="utf-8"))["frame_count"], 16)

            pack = self.run_script(
                SCRIPTS / "gif_director.py",
                "--mode",
                "pack",
                "--image",
                source,
                "--output-dir",
                output_dir,
                "--base-name",
                "campaign",
            )
            self.assertEqual(pack.returncode, 0, pack.stderr + pack.stdout)
            pack_report = json.loads((output_dir / "campaign-pack.json").read_text(encoding="utf-8"))
            self.assertEqual(len(pack_report["outputs"]), 4)
            for item in pack_report["outputs"]:
                self.assertTrue(Path(item["gif"]).exists())

            marketing = self.run_script(
                SCRIPTS / "gif_director.py",
                "--mode",
                "marketing",
                "--image",
                source,
                "--image",
                second,
                "--text",
                "런칭 특가",
                "--output-dir",
                output_dir,
                "--base-name",
                "detail",
                "--preset",
                "detail-page",
            )
            self.assertEqual(marketing.returncode, 0, marketing.stderr + marketing.stdout)
            marketing_report = json.loads((output_dir / "detail-report.json").read_text(encoding="utf-8"))
            self.assertTrue(marketing_report["validation"]["ok"])
            self.assertTrue(Path(marketing_report["contact_sheet"]).exists())

            optimized = output_dir / "detail-optimized.gif"
            optimize_report = output_dir / "detail-optimized.json"
            optimize = self.run_script(
                SCRIPTS / "optimize_gif.py",
                "--input",
                marketing_report["gif"],
                "--output",
                optimized,
                "--report",
                optimize_report,
                "--max-width",
                "420",
                "--max-frames",
                "10",
            )
            self.assertEqual(optimize.returncode, 0, optimize.stderr + optimize.stdout)
            details = json.loads(optimize_report.read_text(encoding="utf-8"))
            self.assertTrue(details["validation"]["ok"])
            self.assertLessEqual(details["validation"]["width"], 420)

            prompt_run = self.run_script(
                SCRIPTS / "gif_director.py",
                "--prompt",
                "상세페이지 중간에 넣을 런칭 특가 GIF. 고급스럽고 너무 정신없지 않게.",
                "--image",
                source,
                "--output-dir",
                output_dir,
                "--base-name",
                "planned-detail",
            )
            self.assertEqual(prompt_run.returncode, 0, prompt_run.stderr + prompt_run.stdout)
            self.assertTrue((output_dir / "planned-detail.gif").exists())
            self.assertTrue((output_dir / "planned-detail-sheet.png").exists())
            self.assertTrue((output_dir / "planned-detail-plan.json").exists())
            self.assertTrue((output_dir / "planned-detail-report.json").exists())
            planned = json.loads((output_dir / "planned-detail-report.json").read_text(encoding="utf-8"))
            self.assertEqual(planned["mode"], "marketing")
            self.assertEqual(planned["plan"]["target"], "detail-page")
            self.assertEqual(planned["plan"]["business_intent"], "launch_offer")
            self.assertEqual(planned["plan"]["constraints"]["no_video"], True)
            self.assertIn("plan_path", planned)
            self.assertIn("gif", planned)
            self.assertIn("contact_sheet", planned)
            self.assertIn("qa_report", planned)
            self.assertTrue(planned["validation"]["ok"])


if __name__ == "__main__":
    unittest.main()

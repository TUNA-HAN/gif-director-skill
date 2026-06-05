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
    width, height = 120, 90
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            pixels.extend((80 + x, 120 + y, 210 - (x // 3)))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(pixels))


class QaReportTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )

    def test_qa_report_combines_plan_render_and_saved_gif_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image = tmp_path / "product.ppm"
            gif = tmp_path / "detail.gif"
            render_report = tmp_path / "detail-render.json"
            plan_path = tmp_path / "plan.json"
            qa_path = tmp_path / "qa.json"
            write_ppm(image)

            render = self.run_script(
                SCRIPTS / "render_gif.py",
                "--image",
                image,
                "--text",
                "런칭 특가",
                "--output",
                gif,
                "--report",
                render_report,
                "--preset",
                "detail-page",
                "--width",
                "240",
                "--height",
                "136",
                "--duration",
                "1.4",
            )
            self.assertEqual(render.returncode, 0, render.stderr + render.stdout)
            plan_path.write_text(
                json.dumps(
                    {
                        "target": "detail-page",
                        "business_intent": "launch_offer",
                        "motion": {"intensity": "subtle"},
                        "constraints": {"no_video": True},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            qa = self.run_script(
                SCRIPTS / "qa_report.py",
                "--gif",
                gif,
                "--render-report",
                render_report,
                "--plan",
                plan_path,
                "--output",
                qa_path,
                "--max-bytes",
                "8000000",
            )
            self.assertEqual(qa.returncode, 0, qa.stderr + qa.stdout)
            report = json.loads(qa_path.read_text(encoding="utf-8"))
            self.assertTrue(report["ok"], report)
            self.assertEqual(report["target"], "detail-page")
            self.assertEqual(report["business_intent"], "launch_offer")
            self.assertEqual(report["motion_intensity"], "subtle")
            self.assertGreater(report["gif"]["frame_count"], 1)
            self.assertFalse(report["caption_metrics"]["clipped"], report)


if __name__ == "__main__":
    unittest.main()

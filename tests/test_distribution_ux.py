import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = ROOT / "skills" / "gif-director" / "scripts" / "install-or-update.ps1"
README = ROOT / "README.md"
SKILL = ROOT / "skills" / "gif-director" / "SKILL.md"


class DistributionUxTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(INSTALL_SCRIPT),
                *args,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
        )

    def test_print_only_installs_or_refreshes_all_supported_agents(self) -> None:
        result = self.run_script("-PrintOnly")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        lines = [line.strip() for line in result.stdout.splitlines() if line.startswith("gh ")]

        self.assertEqual(len(lines), 3)
        self.assertIn(
            "gh skill install TUNA-HAN/gif-director-skill gif-director --agent codex --scope user --force",
            lines,
        )
        self.assertIn(
            "gh skill install TUNA-HAN/gif-director-skill gif-director --agent claude-code --scope user --force",
            lines,
        )
        self.assertIn(
            "gh skill install TUNA-HAN/gif-director-skill gif-director --agent antigravity --scope user --force",
            lines,
        )

    def test_print_only_can_target_codex_only_and_check_updates(self) -> None:
        codex = self.run_script("-Agent", "codex", "-PrintOnly")
        self.assertEqual(codex.returncode, 0, codex.stderr + codex.stdout)
        codex_lines = [line.strip() for line in codex.stdout.splitlines() if line.startswith("gh ")]
        self.assertEqual(
            codex_lines,
            ["gh skill install TUNA-HAN/gif-director-skill gif-director --agent codex --scope user --force"],
        )

        check = self.run_script("-Check", "-PrintOnly")
        self.assertEqual(check.returncode, 0, check.stderr + check.stdout)
        self.assertIn("gh skill update --dry-run gif-director", check.stdout)

    def test_docs_explain_single_command_and_update_path(self) -> None:
        readme = README.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        self.assertIn("skills/gif-director/scripts/install-or-update.ps1", readme)
        self.assertIn("raw.githubusercontent.com/TUNA-HAN/gif-director-skill/main/skills/gif-director/scripts/install-or-update.ps1", readme)
        self.assertIn("gh skill update gif-director", readme)
        self.assertIn("Codex, Claude Code, and Antigravity", readme)
        self.assertIn("scripts/install-or-update.ps1", skill)
        self.assertIn("Install or refresh", skill)


if __name__ == "__main__":
    unittest.main()

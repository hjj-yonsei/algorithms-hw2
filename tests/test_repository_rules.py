import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"


class RepositoryRulesTest(unittest.TestCase):
    def test_copilot_instructions_exist_in_github(self):
        instructions = ROOT / ".github" / "copilot-instructions.md"
        self.assertTrue(instructions.is_file(), ".github/copilot-instructions.md가 필요합니다.")

    def test_src_does_not_use_builtin_dict_set_or_hash(self):
        violations = []

        for path in sorted(SRC_DIR.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: dict")
                elif isinstance(node, ast.Set):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: set")
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in {"dict", "set", "hash"}:
                        violations.append(
                            f"{path.relative_to(ROOT)}:{node.lineno}: {node.func.id}()"
                        )

        self.assertEqual([], violations)

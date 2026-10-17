import unittest

from GraphRevised.proposals.prompt_version import prompt_version


def template_a(text):
    return f"Passage: {text}"


def template_b(text):
    return f"Target passage: {text}"


class PromptVersionTests(unittest.TestCase):
    def test_same_prompt_and_template_give_the_same_version(self):
        self.assertEqual(prompt_version("reader-v1", "rules", template_a), prompt_version("reader-v1", "rules", template_a))

    def test_editing_the_prompt_changes_the_version_without_a_label_bump(self):
        self.assertNotEqual(prompt_version("reader-v1", "rules", template_a), prompt_version("reader-v1", "rules!", template_a))

    def test_editing_the_template_code_changes_the_version(self):
        self.assertNotEqual(prompt_version("reader-v1", "rules", template_a), prompt_version("reader-v1", "rules", template_b))

    def test_reusable_code_names_no_particular_source(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        import re

        names = ("Plutarch", "Antony", "Actium", "Perrin", "Octavian", "Caesar", "Dio", "Cary", "Agrippa",
                 "Cleopatra", "Augustus", "Q160387", "Q41523", "Q185223")
        for path in [*root.glob("proposals/*.py"), *root.glob("identity/*.py"), *root.glob("adapters/*.py"),
                     *root.glob("discovery/*.py"), *root.glob("slices/*.py"), *root.glob("export/*.py"),
                     *root.glob("harvest/*.py"), *root.glob("orchestration/*.py"),
                     *root.glob("capture/*.py"), *root.glob("narrative/*.py")]:
            text = path.read_text(encoding="utf-8")
            for name in names:
                self.assertIsNone(re.search(rf"\b{name}\b", text), f"{name} hardcoded in {path.name}")


if __name__ == "__main__":
    unittest.main()

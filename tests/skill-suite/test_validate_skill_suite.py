from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_skill_suite.py"
SPEC = importlib.util.spec_from_file_location("validate_skill_suite", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
PACKAGE_SCRIPT = ROOT / "scripts" / "package_skill_suite.py"
PACKAGE_SPEC = importlib.util.spec_from_file_location("package_skill_suite", PACKAGE_SCRIPT)
assert PACKAGE_SPEC and PACKAGE_SPEC.loader
PACKAGER = importlib.util.module_from_spec(PACKAGE_SPEC)
PACKAGE_SPEC.loader.exec_module(PACKAGER)


class SkillSuiteValidatorTest(unittest.TestCase):
    def project_from_fixture(self, temporary: Path, name: str) -> Path:
        project = temporary / "project"
        destination = project / "doc" / "project"
        shutil.copytree(ROOT / "tests" / "skill-suite" / "fixtures" / "project-guidance" / name, destination)
        return project

    def capability_manifest(self, *, optional: list[str] | None = None) -> dict:
        return {
            "project_guidance": {"entrypoint": "doc/project/README.md"},
            "skills": {
                "demo": {
                    "dependencies": [],
                    "required_tools": [],
                    "optional_tools": [],
                    "checkout_requirements": {"required": [], "optional": optional or []},
                }
            },
            "profiles": {},
        }

    def test_repository_suite_is_valid(self) -> None:
        self.assertEqual(0, VALIDATOR.main(["--root", str(ROOT), "--check"]))

    def test_generated_metadata_renderer_is_stable(self) -> None:
        rendered = VALIDATOR.render_metadata(
            {
                "display_name": "Example",
                "short_description": "Short",
                "default_prompt": "Use $example.",
            }
        )
        self.assertEqual(
            'interface:\n'
            '  display_name: "Example"\n'
            '  short_description: "Short"\n'
            '  default_prompt: "Use $example."\n',
            rendered,
        )

    def test_deployment_rejects_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "skill" / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "helper.pyc").write_bytes(b"bytecode")
            validation = VALIDATOR.Validation()
            VALIDATOR.validate_deployment_artifacts(root, validation)
            self.assertTrue(validation.errors)

    def test_results_profile_packages_only_declared_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "deployment"
            skills, errors = PACKAGER.package_profile(
                root=ROOT,
                profile_name="results",
                output=output,
                project_root=None,
            )
            self.assertEqual([], errors)
            self.assertEqual(
                ["omnetpp-result-analysis", "omnetpp-result-plotting"], skills
            )
            self.assertFalse(list(output.rglob("*.pyc")))
            self.assertFalse(list(output.rglob("__pycache__")))
            deployment = json.loads(
                (output / ".agents" / "deployment.json").read_text()
            )
            self.assertEqual("results", deployment["profile"])
            self.assertFalse((output / ".agents" / "skill-suite.yaml").exists())
            self.assertTrue(
                (output / ".agents" / "references" / "project-guidance-discovery.md").is_file()
            )
            self.assertTrue((output / ".agents" / "schemas" / "verification-result-v1.schema.json").is_file())

    def test_default_profile_excludes_unavailable_walkthrough(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "deployment"
            skills, errors = PACKAGER.package_profile(
                root=ROOT,
                profile_name="default",
                output=output,
                project_root=ROOT.parent / "inet-pr-doc-project",
            )
            self.assertEqual([], errors)
            self.assertNotIn("inet-80211-walkthrough-writer", skills)
            self.assertFalse(
                (output / ".agents" / "skills" / "inet-80211-walkthrough-writer").exists()
            )
            self.assertTrue((output / "MODELS.md").is_file())
            self.assertTrue((output / ".codex" / "agents" / "inet-reviewer.toml").is_file())

    def test_walkthrough_profile_fails_closed_without_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "deployment"
            skills, errors = PACKAGER.package_profile(
                root=ROOT,
                profile_name="walkthrough",
                output=output,
                project_root=None,
            )
            self.assertEqual([], skills)
            self.assertTrue(any("--project-root is required" in error for error in errors))
            self.assertFalse(output.exists())

    def test_walkthrough_profile_checks_missing_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "deployment"
            skills, errors = PACKAGER.package_profile(
                root=ROOT,
                profile_name="walkthrough",
                output=output,
                project_root=ROOT.parent / "inet-pr-doc-project",
            )
            self.assertEqual([], skills)
            self.assertTrue(any("wifi_analysis.py" in error for error in errors))
            self.assertFalse(output.exists())

    def test_reorganized_guidance_without_markers_is_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            project = self.project_from_fixture(temporary, "reorganized")
            validation = VALIDATOR.Validation()
            VALIDATOR.validate_capabilities(
                ROOT, project, self.capability_manifest(), validation,
                check_tools=False, strict_capabilities=True,
            )
            self.assertEqual([], validation.errors)
            workflow_text = (project / "doc" / "project" / "guidance" / "workflow.md").read_text()
            self.assertIn("MODE=sanitize", workflow_text)
            self.assertIn("tools/check-current-policy", workflow_text)
            self.assertNotIn("TR-FOCUSED-EVIDENCE", workflow_text)

    def test_optional_domain_capability_is_reported_without_invalidating_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            project = self.project_from_fixture(temporary, "optional-domain")
            validation = VALIDATOR.Validation()
            VALIDATOR.validate_capabilities(
                ROOT, project,
                self.capability_manifest(optional=["domain-guidance.md"]),
                validation, check_tools=False, strict_capabilities=True,
            )
            self.assertEqual([], validation.errors)
            self.assertTrue(any("optional capability unavailable" in warning for warning in validation.warnings))

    def test_missing_project_entrypoint_is_a_required_guidance_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            validation = VALIDATOR.Validation()
            VALIDATOR.validate_capabilities(
                ROOT, Path(directory), self.capability_manifest(), validation,
                check_tools=False, strict_capabilities=False,
            )
            self.assertTrue(any("missing project guidance entrypoint" in error for error in validation.errors))

    def test_dependency_cycle_is_rejected(self) -> None:
        manifest = {
            "skills": {
                "a": {"dependencies": ["b"]},
                "b": {"dependencies": ["a"]},
            }
        }
        validation = VALIDATOR.Validation()
        VALIDATOR.validate_dependency_cycles(manifest, validation)
        self.assertTrue(any("skill dependency cycle" in error for error in validation.errors))

    def test_missing_declared_verification_fixture_is_rejected(self) -> None:
        manifest = VALIDATOR.load_yaml(ROOT / ".agents" / "skill-suite.yaml")
        manifest["verification_results"]["required_fixtures"]["unit"].append("missing.log")
        validation = VALIDATOR.Validation()
        VALIDATOR.validate_verification_support(ROOT, manifest, validation)
        self.assertTrue(any("missing verification fixture" in error for error in validation.errors))


if __name__ == "__main__":
    unittest.main()

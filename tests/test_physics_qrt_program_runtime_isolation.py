"""Guard the exact publication runtime while isolating new Physics QRT tools.

These tests inspect the real committed historical publications without writing or
regenerating their manifests, runtime snapshots, HTML, or figures.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Physics.adapter import load as load_physics
from Physics.adapter.qrt_program.qrt_crosswalk import inspect_question
from Physics.adapter.qrt_program.qrt_review_packet import make_packet
from Shared.contracts import digest, file_digest
from Shared.publication_host import storage
from Shared.tools.republish import verify

ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS = (
    ROOT / "Physics/content/relative-motion-g9/publication",
    ROOT / "Physics/content/relative-motion-library/publication",
)
LEGACY_SUBJECT_RUNTIME = {
    "Physics/adapter/__init__.py",
    "Physics/adapter/scenes.py",
    "Physics/adapter/validator.py",
    "Physics/adapter/CoreContracts.json",
    "Physics/run.py",
}


class PhysicsQRTPublicationIsolationTests(unittest.TestCase):
    def test_historical_physics_runtime_dependency_set_is_still_exact(self):
        files = storage.runtime_files(load_physics())
        subject = {path for path in files if path.startswith("Physics/")}
        self.assertEqual(subject, LEGACY_SUBJECT_RUNTIME)
        self.assertTrue(any(k.startswith("Shared/publication_host/") for k in files))
        self.assertNotIn("Physics/adapter/qrt_program/qrt_crosswalk.py", files)
        self.assertTrue(callable(inspect_question))
        self.assertTrue(callable(make_packet))

    def test_both_historical_publications_verify_without_regeneration(self):
        for publication in PUBLICATIONS:
            with self.subTest(publication=publication.name, parent=publication.parent.name):
                self.assertEqual(verify(publication)["status"], "PASS")

    def test_genuine_publication_runtime_digest_mutation_is_detected(self):
        original = storage.runtime_manifest(load_physics())
        original_digest = digest(original)
        target = "Physics/adapter/validator.py"
        self.assertIn("runtime/" + target, {row["path"] for row in original})
        real_hash = file_digest

        def simulated_mutation(path):
            if path.relative_to(ROOT).as_posix() == target:
                return "f" * 64 if real_hash(path) != "f" * 64 else "0" * 64
            return real_hash(path)

        with patch.object(storage, "file_digest", side_effect=simulated_mutation):
            changed = storage.runtime_manifest(load_physics())
        self.assertNotEqual(digest(changed), original_digest)
        self.assertEqual([row["path"] for row in changed], [row["path"] for row in original])


if __name__ == "__main__":
    unittest.main()

import pytest
from dataclasses import dataclass
from typing import Any, Dict

import pytchbuild.tutorialcompiler.gather_tutorials as GT
import pytchbuild.tutorialcompiler.fromgitrepo.errors as TCE


@dataclass
class MockBundle:
    top_level_directory_name: str
    metadata: Dict[str, Any]


def _bundle(dir_name, tutorial_id, language):
    return MockBundle(
        dir_name,
        {"tutorialId": tutorial_id, "language": language},
    )


class TestVerifyUniqueTutorialLanguages:
    def test_translations_accepted(self):
        GT.verify_unique_tutorial_languages([
            _bundle("boing", "boing", "en"),
            _bundle("boing--ga", "boing", "ga"),
            _bundle("boing--de", "boing", "de"),
            _bundle("hello", "hello", "en"),
        ])

    def test_duplicate_rejected(self):
        with pytest.raises(
                TCE.TutorialStructureError,
                match=(
                    'tutorials "boing--ga" and "boing--ga-v2" both have'
                    ' tutorialId "boing" and language "ga"'
                ),
        ):
            GT.verify_unique_tutorial_languages([
                _bundle("boing", "boing", "en"),
                _bundle("boing--ga", "boing", "ga"),
                _bundle("boing--ga-v2", "boing", "ga"),
            ])

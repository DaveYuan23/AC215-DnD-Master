"""
Shared pytest fixtures for all tests.
"""

import sys
from pathlib import Path
import pytest

# Add src/backend-tmp to Python path for imports
backend_path = Path(__file__).parent / "src" / "backend-tmp"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def sample_player():
    """Provide a sample player character for testing."""
    from api.utils.combat_engine import Character
    return Character(
        name="TestKnight",
        char_id=0,
        hp=20,
        ac=18,
        attributes={"STR": 4, "DEX": 2},
        attack_bonus=6,
        damage=10,
        role="player"
    )


@pytest.fixture
def sample_enemy():
    """Provide a sample enemy character for testing."""
    from api.utils.combat_engine import Character
    return Character(
        name="TestGoblin",
        char_id=0,
        hp=12,
        ac=13,
        attributes={"DEX": 3},
        attack_bonus=3,
        damage=6,
        role="enemy"
    )


@pytest.fixture
def sample_characters():
    """Provide a set of test characters (players and enemies)."""
    from api.utils.combat_engine import Character

    players = [
        Character("Knight", 0, 20, 18, {"STR": 4}, 6, 10, "player"),
        Character("Wizard", 1, 15, 12, {"INT": 5}, 3, 8, "player")
    ]

    enemies = [
        Character("Goblin", 0, 12, 13, {"DEX": 3}, 3, 6, "enemy"),
        Character("Troll", 1, 18, 14, {"STR": 4}, 5, 8, "enemy")
    ]

    return {"players": players, "enemies": enemies}


@pytest.fixture
def combat_engine(sample_characters):
    """Provide a CombatEngine instance with test characters."""
    from api.utils.combat_engine import CombatEngine

    return CombatEngine(
        sample_characters["players"],
        sample_characters["enemies"]
    )


@pytest.fixture
def api_test_client():
    """Provide FastAPI TestClient for integration tests."""
    from fastapi.testclient import TestClient
    from api.service import app

    return TestClient(app)


@pytest.fixture
def sample_combat_request():
    """Provide sample combat start request data."""
    return {
        "players": [
            {
                "name": "TestKnight",
                "hp": 20,
                "ac": 18,
                "attributes": {"STR": 4},
                "attack_bonus": 6,
                "damage": 10,
                "role": "player"
            }
        ],
        "enemies": [
            {
                "name": "TestGoblin",
                "hp": 12,
                "ac": 13,
                "attributes": {"DEX": 3},
                "attack_bonus": 3,
                "damage": 6,
                "role": "enemy"
            }
        ]
    }


@pytest.fixture
def sample_rule_validation_request():
    """Provide sample rule validation request data."""
    return {
        "user_input": "I attack the goblin with my sword",
        "context": {
            "in_combat": True,
            "character_class": "Fighter",
            "has_weapon": True
        }
    }


@pytest.fixture
def sample_game_action_request():
    """Provide sample game action request for orchestrator."""
    return {
        "session_id": "test-session-123",
        "user_input": "I examine the ancient door for traps"
    }

import pytest
from dataclasses import dataclass

from ecs import Entity, Component, Query


@dataclass
class Position(Component):
    x: int = 0
    y: int = 0


@dataclass
class Spatial(Position):
    z: int = 0


@dataclass
class Sprite(Component):
    texture: str
    scale: float = 1.0
    rotation: float = 0.0


@dataclass
class Item(Component):
    type: str = "coin"
    quantity: int = 1
    rarity: int = 1


################################################################################


@pytest.fixture
def basic_context():
    context = Entity(
        "context",
        Entity("logo", Position(10, 10)),
        Entity("hero", Position(50, 20), Sprite("hero.png")),
    )

    return Query(context)


@pytest.fixture
def entity_hero(basic_context):
    query = basic_context
    for entity in query._context:
        if entity.id == "hero":
            return entity


@pytest.fixture
def entity_logo(basic_context):
    query = basic_context
    for entity in query._context:
        if entity.id == "logo":
            return entity


@pytest.fixture
def advanced_context(basic_context):
    query = basic_context
    query._context.append(
        Entity(
            "chest",
            Entity("gold", Item("coin", 50, 1)),
            Entity("diamond", Item("gem", 10, 5)),
            Entity("key", Item("key", 1, 2)),
            Entity("book", Item("book", 1, 3)),
            Entity(
                "sack",
                Item("sack", 1, 2),
                Entity("sugar", Item("food", 3, 1)),
                Entity("milk", Item("food", 2, 1)),
                Entity("meat", Item("food", 5, 1)),
                Entity(
                    "bread",
                    Item("food", 1, 1),
                    Entity("gold", Item("coin", 20, 1)),
                ),
            ),
        )
    )

    return query

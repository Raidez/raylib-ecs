from dataclasses import dataclass
from typing import Optional

import pytest

from ecs import Component, Entity, Query


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
def basic_context() -> Query:
    context = Entity(
        "context",
        [],
        [
            Entity("logo", [Position(10, 10)]),
            Entity("hero", [Position(50, 20), Sprite("hero.png")]),
            Entity("chest", [], [
                Entity("gold", [Item("coin", 250, 1)])
            ])
        ],
    )

    return Query(context)


@pytest.fixture
def advanced_context() -> Query:
    context = Entity(
            "context",
            [],
            [
                Entity("logo", [Position(10, 10)]),
                Entity("hero", [Position(50, 20), Sprite("hero.png")]),
                Entity(
                    "chest",
                    [],
                    [
                        Entity("gold", [Item("coin", 50, 1)]),
                        Entity("diamond", [Item("gem", 10, 5)]),
                        Entity("key", [Item("key", 1, 2)]),
                        Entity("book", [Item("book", 1, 3)]),
                        Entity(
                            "sack",
                            [Item("sack", 1, 2)],
                            [
                                Entity("sugar", [Item("food", 3, 1)]),
                                Entity("milk", [Item("food", 2, 1)]),
                                Entity("meat", [Item("food", 5, 1)]),
                                Entity(
                                    "bread",
                                    [Item("food", 1, 1)],
                                    [
                                        Entity("gold", [Item("coin", 20, 1)]),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )

    return Query(context)


@pytest.fixture
def hero(basic_context: Query) -> Optional[Entity]:
    query = basic_context
    for entity in query.context.entities:
        if entity.id == "hero":
            return entity


@pytest.fixture
def logo(basic_context: Query) -> Optional[Entity]:
    query = basic_context
    for entity in query.context.entities:
        if entity.id == "logo":
            return entity


@pytest.fixture
def chest(basic_context: Query) -> Optional[Entity]:
    query = basic_context
    for entity in query.context.entities:
        if entity.id == "chest":
            return entity

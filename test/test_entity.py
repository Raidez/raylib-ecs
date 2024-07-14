from ecs import *
from test import *


def test_basics(hero: Entity, logo: Entity, chest: Entity):
    "check entity basics"

    assert hero.id == "hero"
    assert str(hero) == "hero"
    assert (
        repr(hero)
        == "Entity(hero) : {'position': Position(x=50, y=20), 'sprite': Sprite(texture='hero.png', scale=1.0, rotation=0.0)}"
    )
    assert hero != "hero"
    assert repr(chest) == "Entity(chest) => [Entity(gold) : {'item': Item(type='coin', quantity=250, rarity=1)}]"


def test_has_components(hero: Entity):
    """Check entity.has() function."""

    assert hero.has(Position)
    assert hero.has(Sprite)
    assert not hero.has(Spatial)


def test_add_component(hero: Entity):
    """Check entity.add() function."""
    hero.add(Item("living", 1, 10))

    assert hero.has(Item)


def test_get_component(hero: Entity):
    """Check entity.get() function."""
    assert hero.get(Position) == Position(50, 20)

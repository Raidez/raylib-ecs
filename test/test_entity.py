from ecs import *
from test import *


def test_basics(hero: Entity, logo: Entity, chest: Entity):
    "check entity basics"

    assert hero.id == "hero"
    assert repr(hero) == "hero"
    assert (
        str(hero)
        == "Entity(hero) : {'position': Position(x=50, y=20), 'sprite': Sprite(texture='hero.png', scale=1.0, rotation=0.0)}"
    )
    assert hero != "hero"
    assert str(chest) == "Entity(chest) => [gold]"


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


def test_multi_component_with_same_name():
    """Check if the entity can have multiple components with the same name."""
    @dataclass
    class Gold(Component):
        __id = "gold"
    
    @dataclass
    class gold(Component):
        __id = "gold_as_item"
    
    sack = Entity("sack", [Gold(), gold()])

    assert len(sack._components) == 2
    assert sack.get(Gold) == Gold()
    assert sack.get(gold) == gold()

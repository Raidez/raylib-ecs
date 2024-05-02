import copy
from test import *


def test_basics(entity_hero):
    "check entity basics"
    hero = entity_hero

    assert hero.id == "hero"
    assert repr(hero) == "Entity(hero)"
    assert (
        str(hero)
        == "Entity(hero) : {'position': Position(x=50, y=20), 'sprite': Sprite(texture='hero.png', scale=1.0, rotation=0.0)}"
    )


def test_has_components(entity_hero):
    "check if entity has components with has() method"
    hero = entity_hero

    assert hero.has(Position)
    assert hero.has(Sprite)
    assert not hero.has(Spatial)


def test_contains_components(entity_hero):
    "check if entity has components with __contains__"
    hero = entity_hero

    assert Position in hero
    assert Sprite in hero
    assert Spatial not in hero


def test_shallow_copy(entity_hero):
    "check if entity copy works"
    hero = entity_hero

    hero_copy = copy.copy(hero)
    assert hero_copy.id == hero.id
    assert hero_copy != hero
    assert not hero_copy.has(Position)


def test_deep_copy(entity_hero):
    "check if entity deepcopy works"
    hero = entity_hero

    hero_copy = copy.deepcopy(hero)
    assert hero_copy.id == hero.id
    assert hero_copy == hero
    assert hero_copy.has(Position)

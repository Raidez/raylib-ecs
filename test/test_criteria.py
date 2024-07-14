from ecs import *
from test import *


def test_id_criteria(entity_hero: Entity):
    "check if entity meet criteria with HasId"
    hero = entity_hero

    assert HasId("hero").meet_criteria(hero)


def test_has_components_criteria(entity_hero: Entity):
    "check if entity meet criteria with HasComponent"
    hero = entity_hero

    assert HasComponent(Position).meet_criteria(hero)
    assert HasComponent(Sprite).meet_criteria(hero)
    assert HasNotComponent(Spatial).meet_criteria(hero)


def test_has_value_criteria(entity_hero: Entity):
    "check if entity meet criteria with HasValue"
    hero = entity_hero

    assert HasValue(Position(50, 20)).meet_criteria(hero)


def test_has_multiple_values_criteria(entity_hero: Entity):
    "check if entity meet criteria with HasValues"
    hero = entity_hero

    assert HasValues(position__x=50, position__y=20).meet_criteria(hero)


def test_has_sugar_criteria(entity_hero: Entity):
    "check if entity meet criteria with Has"
    hero = entity_hero

    assert Has(component=Position, id="hero", position__x=50).meet_criteria(hero)
    assert Has(Position(x=50, y=20)).meet_criteria(hero)

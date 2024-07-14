from ecs import *
from test import *


def test_custom_criteria(hero: Entity):
    """Check if entity meet criteria with custom."""
    class IsHeroCriteria(Criteria):
        def meet_criteria(self, entity: Entity) -> bool:
            return entity.id == "hero"

    assert IsHeroCriteria().meet_criteria(hero)


def test_id_criteria(hero: Entity):
    """Check if entity meet criteria with HasId."""

    assert HasId("hero").meet_criteria(hero)


def test_has_component_criteria(hero: Entity):
    """Check if entity meet criteria with HasComponent."""

    assert HasComponent(Position).meet_criteria(hero)
    assert HasComponent(Sprite).meet_criteria(hero)

def test_has_not_component_criteria(hero: Entity):
    """Check if entity meet criteria with HasNotComponent."""

    assert HasNotComponent(Spatial).meet_criteria(hero)
    assert HasNotComponent(Item).meet_criteria(hero)


def test_has_value_criteria(hero: Entity):
    """Check if entity meet criteria with HasValue."""

    assert HasValue(Position(50, 20)).meet_criteria(hero)
    assert HasValue(Sprite("hero.png")).meet_criteria(hero)


def test_has_multiple_values_criteria(hero: Entity):
    """Check if entity meet criteria with HasValues."""

    assert HasValues().meet_criteria(hero) == False
    assert HasValues(position__x__fake=25).meet_criteria(hero) == False

    assert HasValues(position=Position(50, 20)).meet_criteria(hero)
    assert HasValues(position__eq=Position(50, 20)).meet_criteria(hero)
    assert HasValues(position__x=50, position__y=20).meet_criteria(hero)
    assert HasValues(position__x__eq=50, position__y__eq=20).meet_criteria(hero)

    assert HasValues(position__ne=Position(100, 80)).meet_criteria(hero)
    assert HasValues(position__x__ne=100, position__y__ne=80).meet_criteria(hero)

    assert HasValues(position__x__lt=51, position__y__lt=21).meet_criteria(hero)
    assert HasValues(position__x__lte=50, position__y__lte=80).meet_criteria(hero)
    assert HasValues(position__x__gt=49, position__y__gt=19).meet_criteria(hero)
    assert HasValues(position__x__gte=20, position__y__gte=10).meet_criteria(hero)
    assert HasValues(position__x__in=[20, 100], position__y__in=[10, 80]).meet_criteria(hero)


def test_has_criteria(hero: Entity):
    """Check if entity meet criteria with Has."""

    assert Has(HasNotComponent(Spatial), Position, Sprite("hero.png")).meet_criteria(hero)

    assert Has(id="hero").meet_criteria(hero)
    assert Has(component=Position).meet_criteria(hero)
    assert Has(components=[Position, Sprite]).meet_criteria(hero)
    assert Has(component__exclude=Spatial).meet_criteria(hero)
    assert Has(components__exclude=[Spatial, Item]).meet_criteria(hero)
    assert Has(position__x=50, position__y__in=[10, 30]).meet_criteria(hero)

import copy
from typing import Any, Callable, Generator, Self, Type


class Component(object):
    """
    Base class for all components in the ECS system.
    """

    ...


class Entity(object):
    """
    Represents an entity in the ECS system.

    Args:
        - id (str): The identifier for the entity.
        - *args: Variable length list of components or entities to initialize the entity with.

    Attributes:
        - id (str): The unique identifier for the entity.
        - is_active (bool): Flag to indicate if the entity is active.
    """

    def __init__(self, id="", *args: Component | Self):
        self.id = id
        self.is_active = True
        self._entities = []
        self._components = {}

        for arg in args:
            if isinstance(arg, Entity):
                self.append(arg)
            elif isinstance(arg, Component):
                self.add(arg)

    def append(self, entity: Self) -> Self:
        self._entities.append(entity)
        return self

    def extend(self, *entities: Self) -> Self:
        self._entities.extend(entities)
        return self

    def add(self, component: Component) -> Self:
        self._components[component.__class__.__name__.lower()] = component
        return self

    def update(self, *components: Component) -> Self:
        self._components.update(
            {
                component.__class__.__name__.lower(): component
                for component in components
            }
        )
        return self

    def has(self, component: Type[Component]) -> bool:
        return component.__name__.lower() in self._components

    def get(self, component: Type[Component]) -> Component:
        return self._components[component.__name__.lower()]

    # some syntax sugar
    def __getattr__(self, name) -> Any:
        return self._components[name]

    def __contains__(self, component: Type[Component]) -> bool:
        return component.__name__.lower() in self._components

    def __str__(self) -> str:
        s = f"Entity({self.id})"
        if self._components:
            s += f" : {self._components}"
        if self._entities:
            s += f" => {self._entities}"
        return s

    def __repr__(self) -> str:
        return f"Entity({self.id})"

    def __copy__(self):
        return Entity(self.id)

    def __deepcopy__(self, memo):
        E = Entity(self.id)
        for component in self._components.values():
            E.add(copy.copy(component))
        for entity in self._entities:
            E.append(copy.deepcopy(entity))
        return E


class Criteria(object):
    """
    Base class for all criteria in the ECS system.

    Criteria are used to filter entities based on certain conditions.
    """

    def meet_criteria(self, entity: Entity) -> bool:
        return False


class HasId(Criteria):
    def __init__(self, id: str):
        self._id = id

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == self._id


class HasComponent(Criteria):
    def __init__(self, *component_list: Type[Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if not entity.has(component):
                return False
        return True


class HasComponentValue(Criteria):
    def __init__(self, *component_list: Component):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if entity.has(type(component)):
                return entity.get(type(component)) == component
        return True


class HasNotComponent(Criteria):
    def __init__(self, *component_list: Type[Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if entity.has(component):
                return False
        return True


class FilterCriteria(Criteria):
    def __init__(self, filter_fn: Callable[[Entity], bool]):
        self._filter_fn = filter_fn

    def meet_criteria(self, entity: Entity) -> bool:
        return self._filter_fn(entity)


class SugarCriteria(Criteria):
    """
    A class representing criteria using a sugar syntax for easy filtering.

    Examples:
        - SugarCriteria(Position, Sprite, id="hero") => check if entity has both Position and Sprite and entity id is "hero"
        - SugarCriteria(id="hero", position__x__gte=60)) => check if entity id is "hero" and position.x >= 60
    """

    _OPERATOR_LIST = ["eq", "ne", "lt", "gt", "lte", "gte"]

    def __init__(self, *args, **kwargs):
        self._criteria_list = []

        for arg in args:
            if isinstance(arg, Criteria):
                self._criteria_list.append(arg)
            if isinstance(arg, type(Component)):
                self._criteria_list.append(HasComponent(arg))
            if isinstance(arg, Component):
                self._criteria_list.append(HasComponentValue(arg))

        if criteria := kwargs.pop("id", None):  # check entity id
            self._criteria_list.append(HasId(criteria))
        if criteria := kwargs.pop("has", None):  # check if entity has components
            self._criteria_list.append(HasComponent(criteria))
        if criteria := kwargs.pop(
            "has_not", None
        ):  # check if entity has not components
            self._criteria_list.append(HasNotComponent(criteria))
        for key, value in kwargs.items():  # check if entity has components with values
            self._make_filter(key, value)

    def _make_filter(self, key: str, expected_value: Any):
        key_split = key.split("__")
        if len(key_split) == 3:
            component_name, data_name, operator = key_split
        elif len(key_split) == 2:
            component_name, data_name = key_split
            if data_name in SugarCriteria._OPERATOR_LIST:
                operator = data_name
                data_name = ""
            else:
                operator = "eq"
        elif len(key_split) == 1:
            component_name = key_split[0]
            data_name = ""
            operator = "eq"

        def new_fn(entity: Entity) -> bool:
            if component_name in entity._components:
                value = entity._components[component_name]
                if data_name:
                    value = getattr(entity._components[component_name], data_name)
                match operator:
                    case "eq":
                        return value == expected_value
                    case "ne":
                        return value != expected_value
                    case "lt":
                        return value < expected_value
                    case "gt":
                        return value > expected_value
                    case "lte":
                        return value <= expected_value
                    case "gte":
                        return value >= expected_value

            return False

        self._criteria_list.append(FilterCriteria(new_fn))

    def meet_criteria(self, entity: Entity) -> bool:
        return all(criteria.meet_criteria(entity) for criteria in self._criteria_list)


class Query(object):
    """
    A class representing a query in the ECS system.

    Queries are used to call system functions based on criteria.
    """

    def __init__(self, context: Entity):
        self._context = context

    def get(self, *criteria_list: Criteria) -> Entity | None:
        for entity in self._context._entities:
            if Query.check(entity, *criteria_list):
                return entity

    def filter(self, *criteria_list: Criteria) -> Generator[Entity, None, None]:
        for entity in self._context._entities:
            if Query.check(entity, *criteria_list):
                yield entity

    def call(self, fn: Callable, *criteria_list: Criteria) -> Callable:
        def new_fn(*args, **kwargs):
            for entity in self.filter(*criteria_list):
                fn(entity, *args, **kwargs)

        return new_fn

    @staticmethod
    def check(entity: Entity, *criteria_list: Criteria) -> bool:
        return all(criteria.meet_criteria(entity) for criteria in criteria_list)

    @staticmethod
    def decorate(fn: Callable, *criteria_list: Criteria) -> Callable:
        def new_fn(query: Query, *args, **kwargs):
            return query.call(fn, *criteria_list)(*args, **kwargs)

        return new_fn


if __name__ == "__main__":
    from dataclasses import dataclass

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

    ############################################################################

    world = Entity("world", logo := Entity("logo", Position(10, 10)))
    query = Query(world)

    # test 1: check if entity has component
    world.append(hero := Entity("hero", Position(50, 20), Sprite("hero.png")))
    if hero.has(Position):
        assert hero.get(Position).x == 50
    # test 1b: same with syntax sugar
    if Position in hero:
        assert hero.position.y == 20

    # test 2: check if entity has components
    assert Query.check(hero, HasComponent(Position, Sprite))
    assert not Query.check(hero, HasComponent(Spatial))
    assert Query.check(hero, HasComponentValue(Sprite("hero.png")))
    assert not Query.check(hero, HasComponentValue(Position(25, 30)))

    # test 3: found entity by criteria
    assert query.get(HasId("hero")) == hero
    assert all(e in (logo, hero) for e in list(query.filter(HasComponent(Position))))

    # test 4: call function with criteria
    def assert_(cond):
        assert cond

    query.call(lambda e: assert_(e.has(Position)), HasComponent(Position))()
    query.call(lambda e: assert_(e.id == "hero"), HasId("hero"))()
    query.call(
        lambda e, s: assert_(
            f"{s}/{e.get(Sprite).texture}" == "assets/sprite/hero.png"
        ),
        HasComponent(Sprite),
    )("assets/sprite")

    # test 5: call decorated function with extra argument
    def move_position(entity: Entity, offset: int):
        entity.get(Position).x += offset

    move_position_dec = Query.decorate(move_position, HasComponent(Position))
    move_position_dec(query, 10)
    if e := query.get(HasId("hero")):
        assert e.get(Position).x == 60

    # test 6: check entity with exclusive criteria
    assert Query.check(hero, HasNotComponent(Spatial))

    # test 7: use lambda as filter criteria
    assert Query.check(hero, FilterCriteria(lambda e: e.has(Position)))

    # test 8: use syntax sugar for criteria
    assert Query.check(hero, SugarCriteria(has=Position, id="hero", position__x=60))
    assert Query.check(hero, SugarCriteria(Position(x=60, y=20)))

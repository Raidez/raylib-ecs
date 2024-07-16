from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar


############################# abstraction #############################
class Component(ABC):
    @classmethod
    def _get_id(cls) -> str:
        return getattr(cls, f"_{cls.__name__}__id", cls.__name__.lower())


class Criteria(ABC):
    @abstractmethod
    def meet_criteria(self, entity: Entity) -> bool: ...


############################# concrete class #############################
@dataclass
class Group(Component):
    name: str


C = TypeVar("C", bound=Component)


class Entity:
    """
    Represents an entity in the ECS system.

    Attributes:
        id (str): The identifier for the entity.
        is_active (bool): Flag to indicate if the entity is active.
        _components (dict[str, Component]): Map of components, lowercase classname as key.
        entities (list[Entity]): List of sub-entities in the entity.
    """

    def __init__(
        self, id: str, components: list[Component] = [], entities: list[Entity] = []
    ):
        self.id = id
        self.is_active = True
        self._components: dict[str, Component] = {}
        self.entities = entities

        for component in components:
            self.add(component)

    def add(self, component: Component):
        """Add/replace component in the entity."""
        self._components[component._get_id()] = component

    def has(self, component_type: Type[C]) -> bool:
        """Check if the entity has the specified component."""
        for component_name in self._components:
            if component_name == component_type._get_id():
                return True

        return False

    def get(self, component_type: Type[C]) -> C:
        """Return the specified component."""
        return self._components.get(component_type._get_id())

    def clone(self, new_id: str) -> Entity:
        """Return a clone of the entity."""
        return Entity(new_id, list(self._components.values()), self.entities)

    def __eq__(self, other) -> bool:
        if isinstance(other, Entity):
            return (
                self.id == other.id
                and self._components == other._components
                and self.entities == other.entities
            )
        return False

    # for debugging
    def __str__(self) -> str:
        s = f"Entity({self.id})"
        if self._components:
            s += f" : {self._components}"
        if self.entities:
            s += f" => {self.entities}"
        return s

    def __repr__(self) -> str:
        return self.id


class Query:
    def __init__(self, context: Entity):
        self.context = context

    def append(self, entity: Entity):
        """Append an entity to the current context."""
        self.context.entities.append(entity)

    def get(self, criteria_list: list[Criteria] = []) -> Optional[Entity]:
        """Get the first entity whom meet criteria in the tree context."""
        # return all if no criterias provided
        if not len(criteria_list):
            return self.context.entities[0]

        # get all entities in tree
        entities = []
        stack = deque(self.context.entities[:])
        while stack:
            current = stack.popleft()

            if not current.is_active:
                continue

            if len(current.entities):
                stack.extend(current.entities)

            entities.append(current)

        for entity in entities:
            # check if entity meet all criteria
            if all([criteria.meet_criteria(entity) for criteria in criteria_list]):
                return entity

    def filter(self, criteria_list: list[Criteria] = []) -> list[Entity]:
        """Filter entities by criteria in the tree context."""
        # get all entities in tree
        entities = []
        stack = deque(self.context.entities[:])
        while stack:
            current = stack.popleft()

            if not current.is_active:
                continue

            if len(current.entities):
                stack.extend(current.entities)

            entities.append(current)

        # return all if no criterias provided
        if not len(criteria_list):
            return entities

        output = []
        for entity in entities:
            # check if entity meet all criteria
            if all([criteria.meet_criteria(entity) for criteria in criteria_list]):
                output.append(entity)

        return output


############################# criterias definition #############################
class HasId(Criteria):
    """A criteria that checks if an entity has the id."""

    def __init__(self, id: str):
        self.id = id

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == self.id


class HasGroup(Criteria):
    """A criteria that checks if an entity has the group."""

    def __init__(self, group_name: str):
        self.group_name = group_name

    def meet_criteria(self, entity: Entity) -> bool:
        if not entity.has(Group):
            return False

        return entity.get(Group).name == self.group_name


class HasComponent(Criteria):
    """A criteria that checks if an entity has the component."""

    def __init__(self, component_type: Type[Component]):
        self.component_type = component_type

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.has(self.component_type)


class HasNotComponent(Criteria):
    """A criteria that checks if an entity doesn't have the component."""

    def __init__(self, component_type: Type[Component]):
        self.component_type = component_type

    def meet_criteria(self, entity: Entity) -> bool:
        return not entity.has(self.component_type)


class HasValue(Criteria):
    """A criteria that checks if an entity has a component with specified value."""

    def __init__(self, component_value: Component):
        self.component_value = component_value

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.get(type(self.component_value)) == self.component_value


class HasValues(Criteria):
    """
    A criteria that checks if an entity has a list of component values.

    Kwargs:
        Each kwargs key is splitted in 3 parts:
            - The component_name
            - The component sub data
            - The operator in the list => ["eq", "ne", "lt", "gt", "lte", "gte", "in"]
        And the kwargs value is the comparison.

    Exemples:
        HasValues(position=Position(50, 20), position__x=50, position__y__in=[10, 30]).meet_criteria(hero)
    """

    OPERATOR_LIST = ["eq", "ne", "lt", "gt", "lte", "gte", "in"]

    def __init__(self, **kwargs):
        self.criteria_list: list[tuple[str, str, str, Any]] = []
        for key, expected_value in kwargs.items():
            component_name, data_name, operator, *_ = key.split("__") + ["", ""]

            if data_name in self.OPERATOR_LIST:
                operator = data_name
                data_name = ""
            if operator not in self.OPERATOR_LIST:
                operator = "eq"

            self.criteria_list.append(
                (component_name, data_name, operator, expected_value)
            )

    def meet_criteria(self, entity: Entity) -> bool:
        if not len(self.criteria_list):
            return False

        result = []
        for component_name, data_name, operator, expected_value in self.criteria_list:
            if component := entity._components.get(component_name):
                actual_value = getattr(component, data_name, component)

                match operator:
                    case "eq":
                        result.append(actual_value == expected_value)
                    case "ne":
                        result.append(actual_value != expected_value)
                    case "lt":
                        result.append(actual_value < expected_value)
                    case "gt":
                        result.append(actual_value > expected_value)
                    case "lte":
                        result.append(actual_value <= expected_value)
                    case "gte":
                        result.append(actual_value >= expected_value)
                    case "in":
                        result.append(
                            expected_value[0] <= actual_value <= expected_value[1]
                        )

        return all(result)


class Has(Criteria):
    """
    A sugar criteria whom can regroup all criteria.

    Args:
        Criteria: The criteria applied to the entity.
        Component: The component value of the entity.
        Type[Component]: The component type of the entity.

    Exemples:
        Has(HasNotComponent(Spatial), Position, Sprite("hero.png")).meet_criteria(hero)

    Kwargs:
        id (str): The id of the entity.
        component (Type[Component]): The component of the entity.
        components (list[Type[Component]]): The list of component of the entity.

        component__exclude (Type[Component]): The component not in the entity.
        components__exclude (list[Type[Component]]): The list of component not in the entity.
        ...: Same as HasValues criteria for the entity.

    Exemples:
        Has(id="hero").meet_criteria(hero)
        Has(group="adventurers").meet_criteria(hero)
        Has(component=Position).meet_criteria(hero)
        Has(components=[Position, Sprite]).meet_criteria(hero)
        Has(component__exclude=Spatial).meet_criteria(hero)
        Has(components__exclude=[Spatial, Item]).meet_criteria(hero)
        Has(position__x=50, position__y__in=[10, 30]).meet_criteria(hero)
    """

    def __init__(self, *args: Criteria | Component | Type[Component], **kwargs):
        self.criteria_list: list[Criteria] = []

        # args processing
        for arg in args:
            match arg:
                case Criteria():
                    self.criteria_list.append(arg)
                case Component():
                    self.criteria_list.append(HasValue(arg))
                case _ if isinstance(arg, type(Component)):
                    self.criteria_list.append(HasComponent(arg))

        # kwargs processing
        if (criteria := kwargs.pop("id", None)) and isinstance(criteria, str):
            self.criteria_list.append(HasId(criteria))

        if (criteria := kwargs.pop("group", None)) and isinstance(criteria, str):
            self.criteria_list.append(HasGroup(criteria))

        if (criteria := kwargs.pop("component", None)) and isinstance(
            criteria, type(Component)
        ):
            self.criteria_list.append(HasComponent(criteria))

        for criteria in kwargs.pop("components", []):
            if isinstance(criteria, type(Component)):
                self.criteria_list.append(HasComponent(criteria))

        if (criteria := kwargs.pop("component__exclude", None)) and isinstance(
            criteria, type(Component)
        ):
            self.criteria_list.append(HasNotComponent(criteria))

        for criteria in kwargs.pop("components__exclude", []):
            if isinstance(criteria, type(Component)):
                self.criteria_list.append(HasNotComponent(criteria))

        # components values comparison
        if len(kwargs):
            self.criteria_list.append(HasValues(**kwargs))

    def meet_criteria(self, entity: Entity) -> bool:
        return all(criteria.meet_criteria(entity) for criteria in self.criteria_list)

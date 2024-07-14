from __future__ import annotations
import copy
from collections import deque
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

############################# abstraction #############################
class Component(ABC): ...

class Criteria(ABC):
    @abstractmethod
    def meet_criteria(self, entity: Entity) -> bool: ...

############################# concrete class #############################
C = TypeVar('C', bound=Component)

class Entity:
    def __init__(self, id: str, components: list[Component] = [], entities: list[Entity] = []):
        self.id = id
        self.is_active = True
        self._components: dict[str, Component] = {}
        self.entities = entities

        for component in components:
            self.add(component)

    def add(self, component: Component):
        self._components[type(component).__name__.lower()] = component

    def has(self, component_type: Type[C]) -> bool:
        return component_type.__name__.lower() in self._components

    def get(self, component_type: Type[C]) -> C:
        return self._components[component_type.__name__.lower()]

    # for debugging
    def __eq__(self, other) -> bool:
        if isinstance(other, Entity):
            return (
                self.id == other.id
                and self._components == other._components
                and self.entities == other.entities
            )
        return False

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        s = f"Entity({self.id})"
        if self._components:
            s += f" : {self._components}"
        if self.entities:
            s += f" => {self.entities}"
        return s

    # copy and deepcopy
    def __copy__(self):
        return Entity(self.id)

    def __deepcopy__(self, memo):
        E = Entity(self.id)
        for component in self._components.values():
            E.add(copy.copy(component))
        for entity in self.entities:
            E.entities.append(copy.deepcopy(entity))
        return E

class Query:
    def __init__(self, context: Entity):
        self.context = context

    def get(self, criteria_list: list[Criteria] = []) -> Optional[Entity]:
        # get all entities in tree
        entities = []
        stack = self.context.entities[:]
        while stack:
            current = stack.pop()

            if len(current.entities):
                stack.extend(current.entities)

            entities.append(current)

        entities.reverse()

        for entity in entities:
            # check if entity meet all criteria
            if all([criteria.meet_criteria(entity) for criteria in criteria_list]):
                return entity

    def filter(self, criteria_list: list[Criteria] = []) -> list[Entity]:
        # return all if no criterias provided
        if not len(criteria_list):
            return self.context.entities

        # get all entities in tree
        entities = []
        stack = deque(self.context.entities[:])
        while stack:
            current = stack.popleft()

            if len(current.entities):
                stack.extend(current.entities)

            entities.append(current)

        output = []
        for entity in entities:
            # check if entity meet all criteria
            if all([criteria.meet_criteria(entity) for criteria in criteria_list]):
                output.append(entity)

        return output

############################# criterias definition #############################
class HasId(Criteria):
    def __init__(self, id: str):
        self.id = id

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == self.id

class HasComponent(Criteria):
    def __init__(self, component_type: Type[Component]):
        self.component_type = component_type

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.has(self.component_type)

class HasNotComponent(Criteria):
    def __init__(self, component_type: Type[Component]):
        self.component_type = component_type

    def meet_criteria(self, entity: Entity) -> bool:
        return not entity.has(self.component_type)

class HasValue(Criteria):
    def __init__(self, component_value: Component):
        self.component_value = component_value

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.get(type(self.component_value)) == self.component_value

class HasValues(Criteria):
    OPERATOR_LIST = ["eq", "ne", "lt", "gt", "lte", "gte", "in"]

    def __init__(self, **kwargs):
        self.criteria_list: list[tuple[str, str, str, Any]] = []
        for key, expected_value in kwargs.items():
            component_name, data_name, operator, *_ = key.split("__") + ["", ""]

            if operator not in self.OPERATOR_LIST:
                operator = "eq"
            self.criteria_list.append((component_name, data_name, operator, expected_value))

    def meet_criteria(self, entity: Entity) -> bool:
        result = []
        for component_name, data_name, operator, expected_value in self.criteria_list:
            if component := entity._components[component_name.lower()]:
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
                        result.append(expected_value[0] <= actual_value <= expected_value[1])
                    case _:
                        result.append(False)

        return all(result)

class Has(Criteria):
    def __init__(self, *args, **kwargs):
        self.criteria_list: list[Criteria] = []

        # args processing
        for arg in args:
            if isinstance(arg, Criteria):
                self.criteria_list.append(arg)
            if isinstance(arg, type(Component)):
                self.criteria_list.append(HasComponent(arg))
            if isinstance(arg, Component):
                self.criteria_list.append(HasValue(arg))

        # kwargs processing
        if criteria := kwargs.pop("id", None):
            self.criteria_list.append(HasId(criteria))

        if criteria := kwargs.pop("component", None):
            self.criteria_list.append(HasComponent(criteria))

        if (criterias := kwargs.pop("components", None)) and isinstance(criteria, list):
            for criteria in criterias:
                self.criteria_list.append(HasComponent(criteria))

        if criteria := kwargs.pop("component__exclude", None):
            self.criteria_list.append(HasNotComponent(criteria))

        if (criterias := kwargs.pop("components__exclude", None)) and isinstance(criteria, list):
            for criteria in criterias:
                self.criteria_list.append(HasNotComponent(criteria))

        # components values comparison
        self.criteria_list.append(HasValues(**kwargs))

    def meet_criteria(self, entity: Entity) -> bool:
        return all(criteria.meet_criteria(entity) for criteria in self.criteria_list)

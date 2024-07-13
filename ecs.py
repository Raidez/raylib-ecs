from __future__ import annotations
from abc import ABC, abstractmethod
import copy
from typing import Any, Type

############################# abstraction #############################
class Component(ABC):
    def __getattr__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any):
        super().__setattr__(name, value)

class Criteria(ABC):
    @abstractmethod
    def meet_criteria(self, entity: Entity) -> bool: ...

############################# concrete class #############################
class Entity:
    def __init__(self, id: str, components: list[Component] = [], entities: list[Entity] = []):
        self.id = id
        self.is_active = True
        self._components = {}
        self.entities = entities

        for component in components:
            self.add(component)

    def add(self, component: Component):
        self._components[type(component).__name__.lower()] = component

    def has(self, component_type: Type[Component]) -> bool:
        return component_type.__name__.lower() in self._components

    def get(self, component_type: Type[Component]) -> Component:
        return self._components[component_type.__name__.lower()]

    def get_by_name(self, component_name: str) -> Component:
        return self._components[component_name.lower()]

    # for debugging
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

    def filter(self, criterias: list[Criteria] = []) -> list[Entity]:
        # return all if no criterias provided
        if not len(criterias):
            return self.context.entities

        # get all entities in tree
        entities = []
        stack = self.context.entities[:]
        while stack:
            current = stack.pop()

            if len(current.entities):
                stack.extend(current.entities)

            entities.append(current)

        entities.reverse()

        output = []
        for entity in entities:
            # check if entity meet all criteria
            if all([criteria.meet_criteria(entity) for criteria in criterias]):
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
            if component := entity.get_by_name(component_name):
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

if __name__ == "__main__":
    from dataclasses import dataclass

    ### impl ###
    @dataclass
    class Position(Component):
        x: int
        y: int

    ### test ###
    world = Entity("world", [], [
        scarfy := Entity("scarfy", [Position(x=50, y=128)])
    ])

    query = Query(world)
    print(repr(scarfy), scarfy.get(Position), query.filter(), query.filter([HasId("scarfy"), HasComponent(Position), HasValue(Position(50, 128))]))
    print(query.filter([HasValues(position__x__in=[40, 60])]))
    print(query.filter([Has(Position, Position(50, 128), id="scarfy", component=Position, position__x__in=[40, 60])]))

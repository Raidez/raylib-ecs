from typing import Any, Callable, Iterable, Type

import ecs


class HasId(ecs.Criteria):
    "A criteria that checks if an entity has a certain id."

    def __init__(self, id: str):
        self._id = id

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        return entity.id == self._id


class HasComponent(ecs.Criteria):
    "A criteria that checks if an entity has some components."

    def __init__(self, *component_list: Type[ecs.Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        for component in self._component_list:
            if not entity.has(component):
                return False
        return True


class HasComponentValue(ecs.Criteria):
    "A criteria that checks if an entity has some components with a certain value."

    def __init__(self, *component_list: ecs.Component):
        self._component_list = component_list

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        for component in self._component_list:
            if entity.has(type(component)):
                return entity.get(type(component)) == component
        return True


class HasNotComponent(ecs.Criteria):
    "A criteria that checks if an entity doesn't have some components."

    def __init__(self, *component_list: Type[ecs.Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        for component in self._component_list:
            if entity.has(component):
                return False
        return True


class FilterCriteria(ecs.Criteria):
    "A criteria that filters entities based on a filter function."

    def __init__(self, filter_fn: Callable[[ecs.IEntity], bool]):
        self._filter_fn = filter_fn

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        return self._filter_fn(entity)


class SugarCriteria(ecs.Criteria):
    """
    A criteria using a sugar syntax for easy filtering.

    Examples:
        - SugarCriteria(Position, Sprite, id="hero") => check if entity has both Position and Sprite and entity id is "hero"
        - SugarCriteria(id="hero", position__x__gte=60)) => check if entity id is "hero" and position.x >= 60
    """

    _OPERATOR_LIST = ["eq", "ne", "lt", "gt", "lte", "gte"]

    def __init__(self, *args, **kwargs):
        self._criteria_list = []

        for arg in args:
            if isinstance(arg, ecs.Criteria):
                self._criteria_list.append(arg)
            if isinstance(arg, type(ecs.Component)):
                self._criteria_list.append(HasComponent(arg))
            if isinstance(arg, ecs.Component):
                self._criteria_list.append(HasComponentValue(arg))

        if criteria := kwargs.pop("id", None):  # check entity id
            self._criteria_list.append(HasId(criteria))

        if criteria := kwargs.pop("has", None):  # check if entity has components
            if isinstance(criteria, type(ecs.Component)):
                self._criteria_list.append(HasComponent(criteria))
            if isinstance(criteria, Iterable):
                for c in criteria:
                    self._criteria_list.append(HasComponent(c))

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

        def new_fn(entity: ecs.IEntity) -> bool:
            if component_name in entity.components:
                value = entity.components[component_name]
                if data_name:
                    value = getattr(entity.components[component_name], data_name)
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

    def meet_criteria(self, entity: ecs.IEntity) -> bool:
        return all(criteria.meet_criteria(entity) for criteria in self._criteria_list)

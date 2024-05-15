import copy
import warnings
from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Self,
    Type,
)


class Component(ABC):
    "Base class for all components in the ECS system."

    def __getattr__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any):
        super().__setattr__(name, value)


class IEntity(ABC):
    "Base class for all entities in the ECS system."

    @property
    @abstractmethod
    def id(self):
        "The identifier for the entity."
        raise NotImplementedError

    @abstractmethod
    def update(self, *components: Component) -> Self:
        """
        Update the entity with existing components.

        Args:
            *components (Component): The components to be added.

        Chainable.
        """
        raise NotImplementedError

    @abstractmethod
    def has(self, component: Type[Component]) -> bool:
        """
        Check if the entity has a component.

        Args:
            component (Type[Component]): The component to check for.

        Returns:
            bool: True if the entity has the component, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, component: Type[Component]) -> Component:
        """
        Get a component from the entity.

        Args:
            component (Type[Component]): The component to get.

        Returns:
            Component: The component instance.
        """
        raise NotImplementedError


class Entity(IEntity):
    """
    Represents an entity in the ECS system.

    Attributes:
        - id (str): The identifier for the entity.
        - is_active (bool): Flag to indicate if the entity is active.
    """

    def __init__(self, id: str, *args: Component | Self):
        """
        Initializes a new instance of the Entity class with the given id and optional components or other entities.

        Args:
            id (str): The identifier for the entity.
            *args (Component | Entity): Variable length list of components or other entities to initialize the entity with.
        """
        self._id = id
        self.is_active = True
        self._entities = []
        self._components = {}

        for arg in args:
            if isinstance(arg, Entity):
                self.append(arg)
            elif isinstance(arg, Component):
                self.add(arg)

    def append(self, entity: Self) -> Self:
        """
        Appends the given entity to the list of entities.

        Args:
            entity (Entity): The entity to be appended to the list.

        Chainable.
        """
        self._entities.append(entity)
        return self

    def extend(self, *entities: Self) -> Self:
        """
        Extends the current entity with the given entities.

        Args:
            *entities (Entity): Variable length list of entities to extend the current entity with.

        Chainable.
        """
        self._entities.extend(entities)
        return self

    def add(self, component: Component) -> Self:
        """
        Adds a component to the entity.

        Args:
            component (Component): The component to be added.

        Chainable.
        """
        self._components[component.__class__.__name__.lower()] = component
        return self

    # overriding methods
    @property
    def id(self):
        return self._id

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
    def __getattr__(self, name: str) -> Component:
        return self._components[name]

    def __contains__(self, component: Type[Component]) -> bool:
        return component.__name__.lower() in self._components

    def __iter__(self) -> Generator[Self, None, None]:
        yield from self._entities

    def __len__(self) -> int:
        return len(self._entities)

    def __eq__(self, other) -> bool:
        if isinstance(other, Entity):
            return (
                self.id == other.id
                and self._components == other._components
                and self._entities == other._entities
            )
        if isinstance(other, EntityProxy):
            return self.id == other.id
        return False

    # for debugging
    def __str__(self) -> str:
        s = f"Entity({self.id})"
        if self._components:
            s += f" : {self._components}"
        if self._entities:
            s += f" => {self._entities}"
        return s

    def __repr__(self) -> str:
        return f"Entity({self.id})"

    # copy and deepcopy
    def __copy__(self):
        return Entity(self.id)

    def __deepcopy__(self, memo):
        E = Entity(self.id)
        for component in self._components.values():
            E.add(copy.copy(component))
        for entity in self._entities:
            E.append(copy.deepcopy(entity))
        return E


class EntityProxy(IEntity):
    """
    Represents an entity proxy in the ECS system.
    It is used to access components of an entity without modifying out of bounds components.
    """

    def __init__(self, entity: Entity, *components: type[Component]):
        """
        Initializes a new instance of the EntityProxy class.

        Args:
            entity (Entity): The entity to associate with this proxy.
            *components (type[Component]): Variable number of components to include in the proxy.
        """
        self._entity = entity
        self._components = components
        if not len(components):
            self._components = tuple(type(c) for c in entity._components.values())

    # overriding methods
    @property
    def id(self):
        return self._entity.id

    def update(self, *components: Component) -> Self:
        if not all(self._check_component(component) for component in components):
            warnings.warn("Try to reach a component out of bounds")
            return self

        self._entity.update(*components)
        return self

    def has(self, component: Type[Component]) -> bool:
        if not self._check_component_type(component):
            warnings.warn("Try to reach a component out of bounds")
            return False

        return self._entity.has(component)

    def get(self, component: Type[Component]) -> Component:
        if not self._check_component_type(component):
            raise ValueError("Try to reach a component out of bounds")

        return self._entity.get(component)

    # some helper methods
    def _check_component(self, component: Component) -> bool:
        return type(component) in self._components

    def _check_component_type(self, component_type: Type[Component]) -> bool:
        return component_type in self._components

    # some syntax sugar
    def __getattr__(self, name: str) -> Component:
        return self._entity.__getattr__(name)


################################################################################


class Criteria(ABC):
    """
    Base class for all criteria in the ECS system.

    Criteria are used to filter entities based on certain conditions.
    """

    @abstractmethod
    def meet_criteria(self, entity: Entity) -> bool:
        """
        Check if the given entity meets the criteria defined by the subclass.

        Args:
            entity (Entity): The entity to check.

        Returns:
            bool: True if the entity meets the criteria, False otherwise.
        """
        raise NotImplementedError


class HasId(Criteria):
    "A criteria that checks if an entity has a certain id."

    def __init__(self, id: str):
        self._id = id

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == self._id


class HasComponent(Criteria):
    "A criteria that checks if an entity has some components."

    def __init__(self, *component_list: Type[Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if not entity.has(component):
                return False
        return True


class HasComponentValue(Criteria):
    "A criteria that checks if an entity has some components with a certain value."

    def __init__(self, *component_list: Component):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if entity.has(type(component)):
                return entity.get(type(component)) == component
        return True


class HasNotComponent(Criteria):
    "A criteria that checks if an entity doesn't have some components."

    def __init__(self, *component_list: Type[Component]):
        self._component_list = component_list

    def meet_criteria(self, entity: Entity) -> bool:
        for component in self._component_list:
            if entity.has(component):
                return False
        return True


class FilterCriteria(Criteria):
    "A criteria that filters entities based on a filter function."

    def __init__(self, filter_fn: Callable[[Entity], bool]):
        self._filter_fn = filter_fn

    def meet_criteria(self, entity: Entity) -> bool:
        return self._filter_fn(entity)


class SugarCriteria(Criteria):
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
            if isinstance(arg, Criteria):
                self._criteria_list.append(arg)
            if isinstance(arg, type(Component)):
                self._criteria_list.append(HasComponent(arg))
            if isinstance(arg, Component):
                self._criteria_list.append(HasComponentValue(arg))

        if criteria := kwargs.pop("id", None):  # check entity id
            self._criteria_list.append(HasId(criteria))

        if criteria := kwargs.pop("has", None):  # check if entity has components
            if isinstance(criteria, type(Component)):
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


################################################################################


class Query:
    """
    A class representing a query in the ECS system.

    Queries are used to call system functions with entity proxy based on criteria.
    """

    def __init__(self, context: Entity):
        self._context = context

    def _check_arguments(self, *args: Criteria | Type[Component]):
        criteria_list: list[Criteria] = []
        proxy_components: list[Type[Component]] = []

        # args can be a list of criteria or a list of proxy components
        for arg in args:
            if isinstance(arg, Criteria):
                criteria_list.append(arg)
            elif isinstance(arg, type(Component)):
                proxy_components.append(arg)

        # if not criteria_list, add HasComponent for each proxy component
        if not len(criteria_list) and len(proxy_components):
            for proxy_component in proxy_components:
                criteria_list.append(HasComponent(proxy_component))

        return criteria_list, proxy_components

    def get(self, *args: Criteria | Type[Component]) -> EntityProxy | None:
        """
        Returns the first entity that meets all the given criteria.

        Args:
            *args (list[Criteria] | list[type[Component]]): A variable number of criteria or component types.

        Returns:
            EntityProxy | None: The first entity that meets all the given criteria or None if no entity meets all the criteria.
        """
        criteria_list, proxy_component = self._check_arguments(*args)

        # get the first entity that meets all the criteria
        for entity in self._context._entities:
            if len(entity):
                return Query(entity).get(*criteria_list)
            if Query.check(entity, *criteria_list):
                return EntityProxy(entity, *proxy_component)

    def filter(
        self, *args: Criteria | Type[Component]
    ) -> Generator[EntityProxy, None, None]:
        """
        Filters the entities in the context based on the given criteria.

        Args:
            *args (list[Criteria] | list[type[Component]]): A variable number of criteria or component types.

        Yields:
            EntityProxy: An entity that meets all the given criteria.
        """
        criteria_list, proxy_component = self._check_arguments(*args)

        for entity in self._context._entities:
            if Query.check(entity, *criteria_list):
                yield EntityProxy(entity, *proxy_component)
            if len(entity):
                yield from Query(entity).filter(*criteria_list)

    @staticmethod
    def check(entity: Entity, *criteria_list: Criteria) -> bool:
        """
        Check if the given entity meets all the criteria.

        Args:
            entity (Entity): The entity to check.
            *criteria_list (Criteria): Variable number of criteria objects to check against the entity.

        Returns:
            bool: True if the entity meets all the criteria, False otherwise.
        """
        return all(criteria.meet_criteria(entity) for criteria in criteria_list)

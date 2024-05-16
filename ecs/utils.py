import copy
import warnings
from typing import (
    Generator,
    Self,
    Type,
)

import ecs


class Entity(ecs.IEntity):
    """
    Represents an entity in the ECS system.

    Attributes:
        - id (str): The identifier for the entity.
        - is_active (bool): Flag to indicate if the entity is active.
    """

    def __init__(self, id: str, *args: ecs.Component | Self):
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
            elif isinstance(arg, ecs.Component):
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

    def add(self, component: ecs.Component) -> Self:
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

    @property
    def components(self):
        return self._components

    def update(self, *components: ecs.Component) -> Self:
        self._components.update(
            {
                component.__class__.__name__.lower(): component
                for component in components
            }
        )
        return self

    def has(self, component: Type[ecs.Component]) -> bool:
        return component.__name__.lower() in self._components

    def get(self, component: Type[ecs.Component]) -> ecs.Component:
        return self._components[component.__name__.lower()]

    # some syntax sugar
    def __getattr__(self, name: str) -> ecs.Component:
        return self._components[name]

    def __contains__(self, component: Type[ecs.Component]) -> bool:
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


class EntityProxy(ecs.IEntity):
    """
    Represents an entity proxy in the ECS system.
    It is used to access components of an entity without modifying out of bounds components.
    """

    def __init__(self, entity: Entity, *components: type[ecs.Component]):
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

    @property
    def components(self):
        return self._components

    def update(self, *components: ecs.Component) -> Self:
        if not all(self._check_component(component) for component in components):
            warnings.warn("Try to reach a component out of bounds")
            return self

        self._entity.update(*components)
        return self

    def has(self, component: Type[ecs.Component]) -> bool:
        if not self._check_component_type(component):
            warnings.warn("Try to reach a component out of bounds")
            return False

        return self._entity.has(component)

    def get(self, component: Type[ecs.Component]) -> ecs.Component:
        if not self._check_component_type(component):
            raise ValueError("Try to reach a component out of bounds")

        return self._entity.get(component)

    # some helper methods
    def _check_component(self, component: ecs.Component) -> bool:
        return type(component) in self._components

    def _check_component_type(self, component_type: Type[ecs.Component]) -> bool:
        return component_type in self._components

    # some syntax sugar
    def __getattr__(self, name: str) -> ecs.Component:
        return self._entity.__getattr__(name)


class Query:
    """
    A class representing a query in the ECS system.

    Queries are used to call system functions with entity proxy based on criteria.
    """

    def __init__(self, context: Entity):
        self._context = context

    def _check_arguments(self, *args: ecs.Criteria | Type[ecs.Component]):
        criteria_list: list[ecs.Criteria] = []
        proxy_components: list[Type[ecs.Component]] = []

        # args can be a list of criteria or a list of proxy components
        for arg in args:
            if isinstance(arg, ecs.Criteria):
                criteria_list.append(arg)
            elif isinstance(arg, type(ecs.Component)):
                proxy_components.append(arg)

        # if not criteria_list, add HasComponent for each proxy component
        if not len(criteria_list) and len(proxy_components):
            for proxy_component in proxy_components:
                criteria_list.append(ecs.HasComponent(proxy_component))

        return criteria_list, proxy_components

    def get(self, *args: ecs.Criteria | Type[ecs.Component]) -> EntityProxy | None:
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
        self, *args: ecs.Criteria | Type[ecs.Component]
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
    def check(entity: Entity, *criteria_list: ecs.Criteria) -> bool:
        """
        Check if the given entity meets all the criteria.

        Args:
            entity (Entity): The entity to check.
            *criteria_list (Criteria): Variable number of criteria objects to check against the entity.

        Returns:
            bool: True if the entity meets all the criteria, False otherwise.
        """
        return all(criteria.meet_criteria(entity) for criteria in criteria_list)

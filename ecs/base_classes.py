from abc import ABC, abstractmethod
from typing import (
    Any,
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

    @property
    @abstractmethod
    def components(self) -> dict[str, Component]:
        """
        Get all the components of the entity.

        Returns:
            dict[str, Component]: The components of the entity.
        """
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


class Criteria(ABC):
    """
    Base class for all criteria in the ECS system.

    Criteria are used to filter entities based on certain conditions.
    """

    @abstractmethod
    def meet_criteria(self, entity: IEntity) -> bool:
        """
        Check if the given entity meets the criteria defined by the subclass.

        Args:
            entity (Entity): The entity to check.

        Returns:
            bool: True if the entity meets the criteria, False otherwise.
        """
        raise NotImplementedError

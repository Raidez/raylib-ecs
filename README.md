# Quick Start

## Create a context world
First we need to define a global entity (=context) whom hold inside all other entity.
And make a query with the defined context.

```python
from ecs import Entity, Component, Query, SugarCriteria

world = Entity("world")
query = Query(context=world)
```

An entity must have a string identifier.

## Define component
Components are simple classes whom inherit from Component.

```python
class Position(Component):
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y
```

You can use the standard librairie *dataclass* decorator to save some code.

```python
from dataclasses import dataclass

@dataclass
class Position(Component):
    x = 0.0
    y = 0.0
```

## Bake an entity
```python
scarfy = Entity("scarfy", Position(x=50.0, y=220.0))
world.append(scarfy)

# or more condensed
# world.append(Entity("scarfy", Position(x=50.0, y=220.0)))
```

We can also defined all entities inside the world at the initialisation.

```python
world = Entity("world",
    Entity("scarfy", Position(x=50.0, y=220.0)),
)
query = Query(context=world)
```

Keep in mind a entity can have multiple entities (and context world is an entity).

## Call a system
System is a standard function.

```python
def update_position(entity: Entity):
    entity.position.x += 10.0


update_position(scarfy)
```

Be when we have multiple entities, it can be difficult to handle.
So the query system come to rescue !

## The purpose of Query
Remember the query after the context world creation ?
The query have 3 methods (check, get and filter).

We can use get/filter to find an entity with criteria,
let's try it !

```python
def update_position(query: Query):
    for entity in query.filter(SugarCriteria(has=Position)):
        entity.position.x += 10.0

update_position(query)
```

## Choose your criteria
They are many criteria available :
- `HasId("scarfy")` => A criteria that checks if an entity has a certain id.
- `HasComponent(Position)` => A criteria that checks if an entity has some components.
- `HasComponentValue(Position(50, 20))` => A criteria that checks if an entity has some components with a certain value.
- `HasNotComponent(Spatial)` => A criteria that checks if an entity doesn't have some components.
- `FilterCriteria(lambda e: e.has(Position))` => A criteria that filters entities based on a filter function.
- `SugarCriteria(has=Position, id="scarfy", position__x=50)` => A criteria using a sugar syntax for easy filtering.

You can even define your own criteria like that :

```python
class IsScarfy(Criteria):
    "A criteria that checks if an entity has id scarfy."

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == "scarfy"
```

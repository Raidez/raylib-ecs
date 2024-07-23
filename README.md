# ecs.py

## What is ECS?
ECS (Entity Component System) is a composition pattern with a clear separation between data and logic.
1. Entities are used to hold multiple Components.
2. Components are simple data structures.
3. Systems are functions that operate on entities with specific components.

## Quick Start

### Create a world
First, we need to define a global entity (=context) which holds all other entities inside.  
And make a query with the defined context.

```python
from ecs import Entity, Component, Query, HasComponent

world = Entity("world")
query = Query(context=world)
```

An entity must have a string identifier.

### Define component
Components are simple classes that inherit from Component.


```python
class Position(Component):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
```

You can use the standard library *dataclass* decorator to save some code.


```python
from dataclasses import dataclass

@dataclass
class Position(Component):
    x: int = 0
    y: int = 0
```

### Bake an entity
```python
scarfy = Entity("scarfy", [Position(x=50, y=220)])
world.append(scarfy)

# or more condensed
world.append(Entity("scarfy", Position(x=50, y=220)))
```

We can also define all entities inside the world at the initialization.


```python
world = Entity("world", [], [
    Entity("scarfy", Position(x=50, y=220)),
])
query = Query(context=world)
```

Keep in mind an entity can have multiple entities (and context world is an entity).

### Call a system
A system is a standard function.


```python
def update_position(entity: Entity):
    entity.position.x += 10


update_position(scarfy)
```

But when we have multiple entities, it can be difficult to handle.
So the query system comes to the rescue!

### Query your world
Remember the query after the context world creation?  
The query has 3 methods (append, get and filter).

We can use get/filter to find an entity with criteria, let's try it!

```python
def update_position(query: Query):
    for entity in query.filter([HasComponent(Position)]):
        entity.position.x += 10.0

update_position(query)
```

### Choose your criteria
There are many criteria available:
- `HasId("scarfy")` => A criterion that checks if an entity has the id.
- `HasComponent(Position)` => A criterion that checks if an entity has the component.
- `HasNotComponent(Spatial)` => A criterion that checks if an entity doesn't have the component.
- `HasValue(Position(50, 20))` => A criterion that checks if an entity has a component with specified value.
- `HasValues(position__x__in=[50, 60])` => A criterion that checks if an entity has a list of component values.
- `Has(has=Position, id="scarfy", position__x=50)` => A sugar criterion that can regroup all criteria.

You can even define your own criterion like this:

```python
class IsScarfy(Criteria):
    """
    A criterion that checks if an entity has id scarfy.
    Not really useful because HasId already exists.
    """

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == "scarfy"
```

### Pong example
TODO: Rename Criteria to Criterion ?  
TODO: Add pong example

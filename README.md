# ecs.py

## What is ECS ?
ECS (Entity Component System) is a composition pattern with a clear separation between data and logic.
1. Entity are used to held multiple Component.
2. Component are simple data structure.
3. System are function that operate on entities with specific components.

## Quick Start

### Create a world
First we need to define a global entity (=context) whom hold inside all other entity.  
And make a query with the defined context.

```python
from ecs import Entity, Component, Query, HasComponent

world = Entity("world")
query = Query(context=world)
```

An entity must have a string identifier.

### Define component
Components are simple classes whom inherit from Component.

```python
class Position(Component):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
```

You can use the standard librairie *dataclass* decorator to save some code.

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

We can also defined all entities inside the world at the initialisation.

```python
world = Entity("world", [], [
    Entity("scarfy", Position(x=50, y=220)),
])
query = Query(context=world)
```

Keep in mind a entity can have multiple entities (and context world is an entity).

### Call a system
System is a standard function.

```python
def update_position(entity: Entity):
    entity.position.x += 10


update_position(scarfy)
```

But when we have multiple entities, it can be difficult to handle.
So the query system come to rescue !

### Query your world
Remember the query after the context world creation ?  
The query have 3 methods (append, get and filter).

We can use get/filter to find an entity with criteria, let's try it !

```python
def update_position(query: Query):
    for entity in query.filter([HasComponent(Position)]):
        entity.position.x += 10.0

update_position(query)
```

### Choose your criteria
They are many criteria available :
- `HasId("scarfy")` => A criteria that checks if an entity has the id.
- `HasComponent(Position)` => A criteria that checks if an entity has the component.
- `HasNotComponent(Spatial)` => A criteria that checks if an entity doesn't have the component.
- `HasValue(Position(50, 20))` => A criteria that checks if an entity has a component with specified value.
- `HasValues(position__x__in=[50, 60])` => A criteria that checks if an entity has a list of component values.
- `Has(has=Position, id="scarfy", position__x=50)` => A sugar criteria whom can regroup all criteria.

You can even define your own criteria like that :

```python
class IsScarfy(Criteria):
    """
    A criteria that checks if an entity has id scarfy.
    Not really useful because HasId already exists.
    """

    def meet_criteria(self, entity: Entity) -> bool:
        return entity.id == "scarfy"
```

### Pong exemple
TODO

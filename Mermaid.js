```mermaid
classDiagram
    class Owner {
        +name: str
        +daily_time_available: int
        +preferences: dict
    }

    class Pet {
        +name: str
        +species: str
        +age: int
        +health_notes: str
        +tasks: list
    }

    class Task {
        +title: str
        +category: str
        +duration_minutes: int
        +priority: int
        +due_window: str
        +recurring: bool
        +required: bool
    }

    class Scheduler {
        +generate_daily_plan(owner, pet)
        +sort_tasks(tasks)
        +filter_tasks(tasks, time_limit)
        +explain_plan(plan)
    }

    Owner "1" --> "1..*" Pet : manages
    Pet "1" --> "0..*" Task : has
    Scheduler ..> Owner : uses preferences
    Scheduler ..> Pet : reads pet info
    Scheduler ..> Task : evaluates
```

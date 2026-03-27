```mermaid
classDiagram
    class Owner {
        +name: str
        +daily_time_available: int
        +preferences: dict
        +pets: list
        +add_pet(pet)
        +set_preferences(preferences)
    }

    class Pet {
        +name: str
        +species: str
        +age: int
        +health_notes: str
        +owner: Owner
        +tasks: list
        +add_task(task)
        +get_required_tasks()
    }

    class Task {
        +title: str
        +category: str
        +duration_minutes: int
        +priority: int
        +due_window: str
        +recurring: bool
        +required: bool
        +completed: bool
        +pet: Pet
        +is_eligible(time_available)
        +mark_complete()
    }

    class Scheduler {
        +generate_daily_plan(owner)
        +create_plan_item(task, start_time, end_time, reason)
        +sort_tasks(tasks)
        +filter_tasks(tasks, time_limit)
        +explain_plan(plan)
    }

    Owner "1" --> "1..*" Pet : manages
    Pet --> Owner : belongs to
    Pet "1" --> "0..*" Task : has
    Task --> Pet : belongs to
    Scheduler ..> Owner : uses constraints
    Scheduler ..> Pet : schedules for all pets
    Scheduler ..> Task : evaluates
```

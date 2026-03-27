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
        +time: str
        +due_window: str
        +due_date: date
        +frequency: str
        +recurring: bool
        +required: bool
        +completed: bool
        +last_completed_on: date
        +pet: Pet
        +is_eligible(time_available)
        +mark_complete(completed_on)
        +is_due_today(schedule_date)
        +create_next_occurrence(completed_on)
    }

    class Scheduler {
        +last_unscheduled: list
        +generate_daily_plan(owner, schedule_date)
        +create_plan_item(task, start_time, end_time, reason)
        +get_all_tasks(owner)
        +prepare_tasks(tasks, schedule_date)
        +mark_task_complete(task, completed_on)
        +sort_tasks(tasks)
        +sort_by_time(tasks)
        +filter_tasks(tasks, time_limit)
        +filter_tasks_by(tasks, completed, pet_name)
        +detect_time_conflicts(tasks)
        +explain_plan(plan)
        +get_unscheduled_tasks()
        +has_conflict(plan, task, start_minutes, end_minutes)
    }

    Owner "1" --> "1..*" Pet : manages
    Pet --> Owner : belongs to
    Pet "1" --> "0..*" Task : has
    Task --> Pet : belongs to
    Scheduler ..> Owner : uses constraints
    Scheduler ..> Pet : schedules for all pets
    Scheduler ..> Task : evaluates
    Scheduler ..> Task : creates next occurrence
```

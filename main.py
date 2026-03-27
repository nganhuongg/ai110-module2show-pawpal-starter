"""CLI demo for the PawPal+ scheduling system."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_data():
    """Create sample owner, pets, and tasks for a CLI demo."""
    owner = Owner(
        name="Jordan",
        daily_time_available=90,
        preferences={"preferred_categories": ["walk", "medication"]},
    )

    mochi = Pet(name="Mochi", species="dog", age=4, health_notes="Needs daily exercise")
    luna = Pet(name="Luna", species="cat", age=7, health_notes="Takes evening medication")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Add tasks out of chronological order so sorting can be demonstrated clearly.
    mochi.add_task(
        Task(
            title="Lunch feeding",
            category="feeding",
            duration_minutes=10,
            priority=2,
            time="12:00",
            due_window="midday",
            frequency="daily",
            required=True,
        )
    )
    mochi.add_task(
        Task(
            title="Morning walk",
            category="walk",
            duration_minutes=30,
            priority=3,
            time="06:30",
            due_window="morning",
            frequency="daily",
            required=True,
        )
    )
    luna.add_task(
        Task(
            title="Brush coat",
            category="grooming",
            duration_minutes=15,
            priority=1,
            due_window="afternoon",
            time="15:30",
            recurring=False,
            required=False,
        )
    )
    luna.add_task(
        Task(
            title="Vet call",
            category="appointment",
            duration_minutes=20,
            priority=2,
            due_window="midday",
            time="12:00",
            required=True,
        )
    )
    luna.add_task(
        Task(
            title="Evening medication",
            category="medication",
            duration_minutes=5,
            priority=3,
            time="18:00",
            due_window="evening",
            frequency="weekly",
            required=True,
        )
    )

    return owner


def print_task_list(title, tasks):
    """Print a simple list of tasks."""
    print(title)
    print("-" * len(title))
    for task in tasks:
        pet_name = task.pet.name if task.pet else "Unknown pet"
        print(
            f"{task.time} | {pet_name} | {task.title} | "
            f"completed={task.completed}"
        )


def print_schedule(owner):
    """Generate and print today's schedule."""
    scheduler = Scheduler()
    all_tasks = scheduler.get_all_tasks(owner)

    print_task_list("Tasks As Added", all_tasks)
    print()

    print_task_list("Tasks Sorted By Time", scheduler.sort_by_time(all_tasks))
    print()

    print_task_list(
        "Pending Tasks For Mochi",
        scheduler.filter_tasks_by(all_tasks, completed=False, pet_name="Mochi"),
    )
    print()

    print_task_list(
        "Completed Tasks",
        scheduler.filter_tasks_by(all_tasks, completed=True),
    )
    print()

    print("Conflict Warnings")
    print("-----------------")
    conflict_warnings = scheduler.detect_time_conflicts(all_tasks)
    if conflict_warnings:
        for warning in conflict_warnings:
            print(warning)
    else:
        print("No time conflicts detected.")
    print()

    next_task = scheduler.mark_task_complete(
        owner.pets[1].tasks[2],
        completed_on=date(2026, 3, 26),
    )
    print("Next Occurrence Created")
    print("-----------------------")
    if next_task:
        print(
            f"{next_task.time} | {next_task.pet.name} | {next_task.title} | "
            f"due_date={next_task.due_date}"
        )
    print()

    plan = scheduler.generate_daily_plan(owner)

    print("Today's Schedule")
    print("----------------")
    for item in plan:
        task = item["task"]
        pet_name = task.pet.name if task.pet else "Unknown pet"
        print(
            f"{item['start_time']}-{item['end_time']} | {pet_name} | "
            f"{task.title} ({task.due_window}, preferred {task.time})"
        )

    print("\nWhy these tasks were chosen:")
    for explanation in scheduler.explain_plan(plan):
        print(f"- {explanation}")


if __name__ == "__main__":
    demo_owner = build_demo_data()
    print_schedule(demo_owner)

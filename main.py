"""CLI demo for the PawPal+ scheduling system."""

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

    mochi.add_task(
        Task(
            title="Morning walk",
            category="walk",
            duration_minutes=30,
            priority=3,
            due_window="morning",
            recurring=True,
            required=True,
        )
    )
    mochi.add_task(
        Task(
            title="Lunch feeding",
            category="feeding",
            duration_minutes=10,
            priority=2,
            due_window="midday",
            recurring=True,
            required=True,
        )
    )
    luna.add_task(
        Task(
            title="Evening medication",
            category="medication",
            duration_minutes=5,
            priority=3,
            due_window="evening",
            recurring=True,
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
            recurring=False,
            required=False,
        )
    )

    return owner


def print_schedule(owner):
    """Generate and print today's schedule."""
    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(owner)

    print("Today's Schedule")
    print("----------------")
    for item in plan:
        task = item["task"]
        pet_name = task.pet.name if task.pet else "Unknown pet"
        print(
            f"{item['start_time']}-{item['end_time']} | {pet_name} | "
            f"{task.title} ({task.due_window})"
        )

    print("\nWhy these tasks were chosen:")
    for explanation in scheduler.explain_plan(plan):
        print(f"- {explanation}")


if __name__ == "__main__":
    demo_owner = build_demo_data()
    print_schedule(demo_owner)

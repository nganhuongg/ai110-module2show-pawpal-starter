"""Tests for core PawPal+ task and pet behavior."""

from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    """Calling mark_complete should update the task completion state."""
    task = Task(
        title="Give medicine",
        category="medication",
        duration_minutes=5,
        priority=3,
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_mark_task_complete_creates_next_daily_occurrence():
    """Completing a daily task should create a new task for the next day."""
    pet = Pet(name="Mochi", species="dog", age=4)
    scheduler = Scheduler()
    task = Task(
        title="Breakfast",
        category="feeding",
        duration_minutes=10,
        priority=2,
        frequency="daily",
    )
    pet.add_task(task)

    next_task = scheduler.mark_task_complete(task, completed_on=date(2026, 3, 26))

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 27)
    assert next_task.pet is pet
    assert len(pet.tasks) == 2


def test_mark_task_complete_creates_next_weekly_occurrence():
    """Completing a weekly task should create a new task for the next week."""
    pet = Pet(name="Luna", species="cat", age=7)
    scheduler = Scheduler()
    task = Task(
        title="Medication refill",
        category="medication",
        duration_minutes=15,
        priority=3,
        frequency="weekly",
    )
    pet.add_task(task)

    next_task = scheduler.mark_task_complete(task, completed_on=date(2026, 3, 26))

    assert next_task is not None
    assert next_task.due_date == date(2026, 4, 2)


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should increase the number of stored tasks."""
    pet = Pet(name="Mochi", species="dog", age=4)
    initial_count = len(pet.tasks)

    pet.add_task(
        Task(
            title="Morning walk",
            category="walk",
            duration_minutes=30,
            priority=2,
        )
    )

    assert len(pet.tasks) == initial_count + 1

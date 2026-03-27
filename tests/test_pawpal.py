"""Tests for core PawPal+ task and pet behavior."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task


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

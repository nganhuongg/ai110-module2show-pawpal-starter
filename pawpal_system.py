"""Core classes for the PawPal+ scheduling system."""


class Owner:
    """Represents a pet owner and their care preferences."""

    def __init__(self, name, daily_time_available, preferences=None):
        self.name = name
        self.daily_time_available = daily_time_available
        self.preferences = preferences or {}
        self.pets = []

    def add_pet(self, pet):
        """Add a pet to the owner's list and link the pet back to the owner."""
        pet.owner = self
        self.pets.append(pet)

    def set_preferences(self, preferences):
        """Update the owner's care preferences."""
        self.preferences = preferences


class Pet:
    """Represents a pet and the care tasks associated with it."""

    def __init__(self, name, species, age, health_notes="", owner=None):
        self.name = name
        self.species = species
        self.age = age
        self.health_notes = health_notes
        self.owner = owner
        self.tasks = []

    def add_task(self, task):
        """Add a care task for this pet and link the task back to the pet."""
        task.pet = self
        self.tasks.append(task)

    def get_required_tasks(self):
        """Return only tasks that are required."""
        return [task for task in self.tasks if task.required]


class Task:
    """Represents a single pet care task."""

    def __init__(
        self,
        title,
        category,
        duration_minutes,
        priority,
        due_window="anytime",
        recurring=False,
        required=False,
        pet=None,
    ):
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.due_window = due_window
        self.recurring = recurring
        self.required = required
        self.pet = pet
        self.completed = False

    def is_eligible(self, time_available):
        """Check whether the task can fit in the available time."""
        return self.duration_minutes <= time_available

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True


class Scheduler:
    """Builds a daily plan based on tasks, time, and preferences."""

    def generate_daily_plan(self, owner):
        """Create a daily plan across all pets owned by one owner."""
        all_tasks = self.sort_tasks(self.get_all_tasks(owner))
        selected_tasks = self.filter_tasks(all_tasks, owner.daily_time_available)

        plan = []
        current_time = 0

        for task in selected_tasks:
            start_time = self._format_minutes(current_time)
            current_time += task.duration_minutes
            end_time = self._format_minutes(current_time)
            reason = self._build_reason(task, owner.preferences)
            plan.append(self.create_plan_item(task, start_time, end_time, reason))

        return plan

    def create_plan_item(self, task, start_time, end_time, reason):
        """Create one schedule entry for the final plan."""
        return {
            "task": task,
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason,
        }

    def get_all_tasks(self, owner):
        """Collect all tasks across the owner's pets."""
        tasks = []
        for pet in owner.pets:
            tasks.extend(pet.tasks)
        return tasks

    def sort_tasks(self, tasks):
        """Sort tasks by required status first, then priority, then duration."""
        return sorted(
            tasks,
            key=lambda task: (not task.required, -task.priority, task.duration_minutes),
        )

    def filter_tasks(self, tasks, time_limit):
        """Filter tasks that can fit within the given time limit."""
        selected_tasks = []
        remaining_time = time_limit

        for task in tasks:
            if task.is_eligible(remaining_time):
                selected_tasks.append(task)
                remaining_time -= task.duration_minutes

        return selected_tasks

    def explain_plan(self, plan):
        """Return a readable explanation for why tasks were chosen."""
        explanations = []
        for item in plan:
            task = item["task"]
            pet_name = task.pet.name if task.pet else "Unknown pet"
            explanations.append(
                f"{task.title} for {pet_name} from {item['start_time']} to "
                f"{item['end_time']}: {item['reason']}"
            )
        return explanations

    def _build_reason(self, task, preferences):
        """Create a short explanation for why a task was scheduled."""
        reason_parts = [f"priority {task.priority}"]

        if task.required:
            reason_parts.append("required task")

        preferred_categories = preferences.get("preferred_categories", [])
        if task.category in preferred_categories:
            reason_parts.append("matches owner preferences")

        return ", ".join(reason_parts)

    def _format_minutes(self, minutes):
        """Convert minutes from the start of the day into an HH:MM string."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

"""Core class skeletons for the PawPal+ scheduling system."""


class Owner:
    """Represents a pet owner and their care preferences."""

    def __init__(self, name, daily_time_available, preferences=None):
        self.name = name
        self.daily_time_available = daily_time_available
        self.preferences = preferences or {}
        self.pets = []

    def add_pet(self, pet):
        """Add a pet to the owner's list."""
        pass

    def set_preferences(self, preferences):
        """Update the owner's care preferences."""
        pass


class Pet:
    """Represents a pet and the care tasks associated with it."""

    def __init__(self, name, species, age, health_notes=""):
        self.name = name
        self.species = species
        self.age = age
        self.health_notes = health_notes
        self.tasks = []

    def add_task(self, task):
        """Add a care task for this pet."""
        pass

    def get_required_tasks(self):
        """Return only tasks that are required."""
        pass


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
    ):
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.due_window = due_window
        self.recurring = recurring
        self.required = required

    def is_eligible(self, time_available):
        """Check whether the task can fit in the available time."""
        pass


class Scheduler:
    """Builds a daily plan based on tasks, time, and preferences."""

    def __init__(self):
        self.plan = []

    def generate_daily_plan(self, owner, pet):
        """Create a daily plan for one pet."""
        pass

    def sort_tasks(self, tasks):
        """Sort tasks by scheduling importance."""
        pass

    def filter_tasks(self, tasks, time_limit):
        """Filter tasks that can fit within the given time limit."""
        pass

    def explain_plan(self, plan):
        """Return an explanation for why tasks were chosen."""
        pass

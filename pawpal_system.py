"""Core classes for the PawPal+ scheduling system."""

from datetime import date, timedelta


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
        time="00:00",
        due_window="anytime",
        due_date=None,
        frequency="none",
        recurring=False,
        required=False,
        pet=None,
    ):
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.time = time
        self.due_window = due_window
        self.due_date = due_date or date.today()
        self.frequency = self._normalize_frequency(frequency, recurring)
        self.recurring = self.frequency in {"daily", "weekly"}
        self.required = required
        self.pet = pet
        self.completed = False
        self.last_completed_on = None

    def is_eligible(self, time_available):
        """Check whether the task can fit in the available time."""
        return not self.completed and self.duration_minutes <= time_available

    def mark_complete(self, completed_on=None):
        """Mark the task as completed."""
        self.completed = True
        self.last_completed_on = completed_on or date.today()

    def is_due_today(self, schedule_date=None):
        """Return whether the task should be considered for today's plan."""
        current_day = schedule_date or date.today()
        return not self.completed and self.due_date <= current_day

    def create_next_occurrence(self, completed_on=None):
        """Create the next dated task instance for daily or weekly frequencies.

        The returned task copies the current task's scheduling details and shifts
        its due date forward by one day for daily tasks or seven days for weekly
        tasks. Non-recurring tasks return ``None``.
        """
        if self.frequency not in {"daily", "weekly"}:
            return None

        completion_day = completed_on or date.today()
        days_until_next = 1 if self.frequency == "daily" else 7
        next_due_date = completion_day + timedelta(days=days_until_next)

        return Task(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            due_window=self.due_window,
            due_date=next_due_date,
            frequency=self.frequency,
            required=self.required,
        )

    def _normalize_frequency(self, frequency, recurring):
        """Convert legacy recurring flags into explicit frequencies."""
        if frequency in {"daily", "weekly"}:
            return frequency
        if recurring:
            return "daily"
        return "none"


class Scheduler:
    """Builds a daily plan based on tasks, time, and preferences."""

    WINDOW_RANGES = {
        "morning": (360, 720),
        "midday": (720, 900),
        "afternoon": (900, 1080),
        "evening": (1080, 1260),
        "anytime": (360, 1260),
    }

    WINDOW_ORDER = {
        "morning": 0,
        "midday": 1,
        "afternoon": 2,
        "evening": 3,
        "anytime": 4,
    }

    def __init__(self):
        self.last_unscheduled = []

    def generate_daily_plan(self, owner, schedule_date=None):
        """Create a daily plan across all pets owned by one owner."""
        self.last_unscheduled = []
        current_day = schedule_date or date.today()
        all_tasks = self.prepare_tasks(self.get_all_tasks(owner), current_day)
        selected_tasks = self.filter_tasks(
            self.sort_tasks(all_tasks), owner.daily_time_available
        )

        plan = []
        current_time = self.WINDOW_RANGES["anytime"][0]

        for task in selected_tasks:
            proposed_start = self._find_start_time(task, current_time)
            proposed_end = proposed_start + task.duration_minutes

            if self.has_conflict(plan, task, proposed_start, proposed_end):
                self.last_unscheduled.append(
                    self._build_unscheduled_item(
                        task,
                        "time conflict with another scheduled task",
                    )
                )
                continue

            start_time = self._format_minutes(proposed_start)
            end_time = self._format_minutes(proposed_end)
            reason = self._build_reason(task, owner.preferences)
            plan.append(self.create_plan_item(task, start_time, end_time, reason))
            current_time = proposed_end

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

    def prepare_tasks(self, tasks, schedule_date=None):
        """Keep only tasks that are due and not already complete for the day."""
        prepared_tasks = []

        for task in tasks:
            if task.is_due_today(schedule_date):
                prepared_tasks.append(task)
            else:
                self.last_unscheduled.append(
                    self._build_unscheduled_item(task, "already completed")
                )

        return prepared_tasks

    def mark_task_complete(self, task, completed_on=None):
        """Mark a task complete and append its next recurring instance.

        This method updates the current task's completion state, asks the task to
        generate its next occurrence when its frequency is daily or weekly, and
        adds that new task back to the same pet so future schedules can include it.
        """
        completion_day = completed_on or date.today()
        task.mark_complete(completion_day)
        next_task = task.create_next_occurrence(completion_day)

        if next_task and task.pet:
            task.pet.add_task(next_task)

        return next_task

    def sort_tasks(self, tasks):
        """Sort tasks by required status, preferred time, priority, and duration."""
        return sorted(
            tasks,
            key=lambda task: (
                not task.required,
                self.WINDOW_ORDER.get(task.due_window, self.WINDOW_ORDER["anytime"]),
                task.time,
                -task.priority,
                task.duration_minutes,
            ),
        )

    def sort_by_time(self, tasks):
        """Sort tasks by their HH:MM time string."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_tasks(self, tasks, time_limit):
        """Filter tasks that can fit within the given time limit."""
        selected_tasks = []
        remaining_time = time_limit

        for task in tasks:
            if task.is_eligible(remaining_time):
                selected_tasks.append(task)
                remaining_time -= task.duration_minutes
            else:
                self.last_unscheduled.append(
                    self._build_unscheduled_item(task, "not enough remaining time")
                )

        return selected_tasks

    def filter_tasks_by(self, tasks, completed=None, pet_name=None):
        """Filter tasks by completion status, pet name, or both.

        Passing ``completed`` keeps only tasks with that completion state.
        Passing ``pet_name`` keeps only tasks owned by the matching pet.
        If both filters are provided, a task must satisfy both conditions.
        """
        filtered_tasks = tasks

        if completed is not None:
            filtered_tasks = [
                task for task in filtered_tasks if task.completed == completed
            ]

        if pet_name is not None:
            filtered_tasks = [
                task
                for task in filtered_tasks
                if task.pet and task.pet.name.lower() == pet_name.lower()
            ]

        return filtered_tasks

    def detect_time_conflicts(self, tasks):
        """Return warning messages for tasks whose time ranges overlap.

        Tasks are first sorted by their ``HH:MM`` start time. The method then
        compares each task only with later tasks that could still overlap, which
        keeps the logic lightweight while still catching same-time and partial
        overlap conflicts.
        """
        warnings = []
        sorted_tasks = self.sort_by_time(tasks)

        for index, first_task in enumerate(sorted_tasks):
            first_start = self._parse_time(first_task.time)
            first_end = first_start + first_task.duration_minutes

            for second_task in sorted_tasks[index + 1 :]:
                second_start = self._parse_time(second_task.time)
                second_end = second_start + second_task.duration_minutes

                if second_start >= first_end:
                    break

                if first_start < second_end and second_start < first_end:
                    warnings.append(
                        self._build_conflict_warning(
                            first_task,
                            second_task,
                            first_start,
                            first_end,
                            second_start,
                            second_end,
                        )
                    )

        return warnings

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

        if task.recurring:
            reason_parts.append("recurring task")

        preferred_categories = preferences.get("preferred_categories", [])
        if task.category in preferred_categories:
            reason_parts.append("matches owner preferences")

        return ", ".join(reason_parts)

    def get_unscheduled_tasks(self):
        """Return tasks that were skipped and the reason why."""
        return list(self.last_unscheduled)

    def has_conflict(self, plan, task, start_minutes, end_minutes):
        """Check whether the task overlaps the preferred time window."""
        window_start, window_end = self.WINDOW_RANGES.get(
            task.due_window, self.WINDOW_RANGES["anytime"]
        )

        if start_minutes < window_start or end_minutes > window_end:
            return True

        for item in plan:
            existing_start = self._parse_time(item["start_time"])
            existing_end = self._parse_time(item["end_time"])
            if start_minutes < existing_end and end_minutes > existing_start:
                return True

        return False

    def _build_unscheduled_item(self, task, reason):
        """Create one explanation for a skipped task."""
        pet_name = task.pet.name if task.pet else "Unknown pet"
        return {
            "task": task,
            "pet": pet_name,
            "reason": reason,
        }

    def _build_conflict_warning(
        self,
        first_task,
        second_task,
        first_start,
        first_end,
        second_start,
        second_end,
    ):
        """Create a readable warning for two overlapping tasks."""
        first_pet = first_task.pet.name if first_task.pet else "Unknown pet"
        second_pet = second_task.pet.name if second_task.pet else "Unknown pet"

        overlap_start = self._format_minutes(max(first_start, second_start))
        overlap_end = self._format_minutes(min(first_end, second_end))

        return (
            f"Warning: {first_task.title} for {first_pet} overlaps with "
            f"{second_task.title} for {second_pet} from {overlap_start} to "
            f"{overlap_end}."
        )

    def _find_start_time(self, task, current_time):
        """Find the next valid start time based on the task's preferred window."""
        window_start, _ = self.WINDOW_RANGES.get(
            task.due_window, self.WINDOW_RANGES["anytime"]
        )
        return max(current_time, window_start)

    def _format_minutes(self, minutes):
        """Convert minutes from the start of the day into an HH:MM string."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def _parse_time(self, time_string):
        """Convert an HH:MM string back into minutes."""
        hours, mins = time_string.split(":")
        return int(hours) * 60 + int(mins)

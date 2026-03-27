from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def build_task_rows(tasks):
    """Convert task objects into dashboard-friendly table rows."""
    rows = []
    for task in tasks:
        pet_name = task.pet.name if task.pet else "Unknown pet"
        rows.append(
            {
                "time": task.time,
                "pet": pet_name,
                "task": task.title,
                "category": task.category,
                "duration": task.duration_minutes,
                "priority": task.priority,
                "time_window": task.due_window,
                "frequency": task.frequency,
                "status": "Completed" if task.completed else "Pending",
                "due_date": task.due_date.isoformat(),
            }
        )
    return rows


def build_pet_rows(owner):
    """Create summary rows for each pet."""
    return [
        {
            "name": pet.name,
            "species": pet.species,
            "age": pet.age,
            "health_notes": pet.health_notes or "None",
            "tasks": len(pet.tasks),
        }
        for pet in owner.pets
    ]


def count_pending_tasks(tasks):
    """Return the number of incomplete tasks."""
    return sum(not task.completed for task in tasks)


if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(
        name="Jordan",
        daily_time_available=90,
        preferences={},
    )

owner = st.session_state["owner"]
scheduler = Scheduler()
all_tasks = scheduler.get_all_tasks(owner)
task_conflicts = scheduler.detect_time_conflicts(all_tasks)


st.title("🐾 PawPal+")
st.caption(
    "A pet care dashboard for organizing pets, tracking tasks, and generating a"
    " smarter daily schedule."
)

with st.expander("About PawPal+", expanded=False):
    st.markdown(
        """
        PawPal+ helps a pet owner organize care tasks across multiple pets, sort
        priorities by time, detect conflicts, and build a practical daily plan.
        """
    )


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Pets", len(owner.pets))
metric_col2.metric("Total Tasks", len(all_tasks))
metric_col3.metric("Pending Tasks", count_pending_tasks(all_tasks))
metric_col4.metric("Conflicts", len(task_conflicts))

st.divider()


st.subheader("Owner Setup")
owner_col1, owner_col2 = st.columns([2, 1])
with owner_col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with owner_col2:
    owner.daily_time_available = int(
        st.number_input(
            "Daily time available (minutes)",
            min_value=15,
            max_value=600,
            value=owner.daily_time_available,
            step=15,
        )
    )

st.info("Set how much time you have today so PawPal+ can build a realistic plan.")

st.divider()


left_panel, right_panel = st.columns([1, 1])

with left_panel:
    st.subheader("Pets")
    with st.form("add_pet_form"):
        pet_name = st.text_input("Pet name", value="Mochi")
        pet_col1, pet_col2 = st.columns(2)
        with pet_col1:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        with pet_col2:
            age = st.number_input("Age", min_value=0, max_value=30, value=4)
        health_notes = st.text_input("Health notes", value="")
        add_pet_submitted = st.form_submit_button("Add pet")

    if add_pet_submitted:
        new_pet = Pet(
            name=pet_name,
            species=species,
            age=int(age),
            health_notes=health_notes,
        )
        owner.add_pet(new_pet)
        st.success(f"Added {new_pet.name} to {owner.name}'s pets.")
        all_tasks = scheduler.get_all_tasks(owner)
        task_conflicts = scheduler.detect_time_conflicts(all_tasks)

    pet_rows = build_pet_rows(owner)
    if pet_rows:
        st.table(pet_rows)
    else:
        st.info("No pets yet. Add a pet to start building your care dashboard.")

with right_panel:
    st.subheader("Add Task")
    if owner.pets:
        selected_pet_name = st.selectbox(
            "Choose a pet",
            options=[pet.name for pet in owner.pets],
        )
        selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

        with st.form("add_task_form"):
            task_title = st.text_input("Task name", value="Morning walk")
            task_col1, task_col2 = st.columns(2)
            with task_col1:
                category = st.selectbox(
                    "Category",
                    [
                        "walk",
                        "feeding",
                        "medication",
                        "grooming",
                        "appointment",
                        "other",
                    ],
                )
                duration = st.number_input(
                    "Duration (minutes)",
                    min_value=1,
                    max_value=240,
                    value=20,
                )
                priority_label = st.selectbox(
                    "Priority",
                    ["low", "medium", "high"],
                    index=2,
                )
            with task_col2:
                task_time = st.text_input("Start time (HH:MM)", value="08:00")
                due_window = st.selectbox(
                    "Preferred time of day",
                    ["morning", "midday", "afternoon", "evening", "anytime"],
                    index=0,
                )
                frequency = st.selectbox(
                    "Repeats",
                    ["none", "daily", "weekly"],
                    index=1,
                )

            required = st.checkbox("Required today", value=True)
            add_task_submitted = st.form_submit_button("Add task")

        if add_task_submitted:
            priority_map = {"low": 1, "medium": 2, "high": 3}
            new_task = Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=priority_map[priority_label],
                time=task_time,
                due_window=due_window,
                frequency=frequency,
                required=required,
            )
            selected_pet.add_task(new_task)
            st.success(f"Added task '{new_task.title}' for {selected_pet.name}.")
            all_tasks = scheduler.get_all_tasks(owner)
            task_conflicts = scheduler.detect_time_conflicts(all_tasks)
    else:
        st.info("Add a pet first, then you can assign tasks.")

st.divider()


st.subheader("Task Dashboard")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_task_pet_filter = st.selectbox(
        "Filter by pet",
        options=["All pets"] + [pet.name for pet in owner.pets] if owner.pets else ["All pets"],
    )
with filter_col2:
    status_filter = st.selectbox(
        "Filter by status",
        options=["all", "pending", "completed"],
    )

completed_filter = None
if status_filter == "pending":
    completed_filter = False
elif status_filter == "completed":
    completed_filter = True

pet_name_filter = None
if selected_task_pet_filter != "All pets":
    pet_name_filter = selected_task_pet_filter

sorted_tasks = scheduler.sort_by_time(all_tasks)
visible_tasks = scheduler.filter_tasks_by(
    sorted_tasks,
    completed=completed_filter,
    pet_name=pet_name_filter,
)

if task_conflicts:
    st.warning("Some tasks overlap in time. Review the warnings below before scheduling.")
    for warning in task_conflicts:
        st.write(f"- {warning}")
else:
    st.success("No task conflicts detected.")

task_rows = build_task_rows(visible_tasks)
if task_rows:
    st.table(task_rows)
else:
    st.info("No tasks match the current filters.")

st.divider()


st.subheader("Today's Smart Schedule")
st.caption("Generate a plan based on priority, available time, time windows, and conflicts.")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_daily_plan(owner, schedule_date=date.today())

    if plan:
        schedule_rows = []
        total_minutes = 0

        for item in plan:
            task = item["task"]
            pet_name = task.pet.name if task.pet else "Unknown pet"
            total_minutes += task.duration_minutes
            schedule_rows.append(
                {
                    "start": item["start_time"],
                    "end": item["end_time"],
                    "pet": pet_name,
                    "task": task.title,
                    "preferred_time": task.time,
                    "time_window": task.due_window,
                    "reason": item["reason"],
                }
            )

        st.success(
            f"Schedule generated successfully. {len(plan)} tasks scheduled in "
            f"{total_minutes} minutes."
        )
        st.table(schedule_rows)

        with st.expander("Why these tasks were chosen", expanded=True):
            for explanation in scheduler.explain_plan(plan):
                st.write(f"- {explanation}")

        unscheduled = scheduler.get_unscheduled_tasks()
        if unscheduled:
            st.warning("Some tasks could not be scheduled.")
            unscheduled_rows = [
                {
                    "pet": item["pet"],
                    "task": item["task"].title,
                    "reason": item["reason"],
                }
                for item in unscheduled
            ]
            st.table(unscheduled_rows)
    else:
        st.warning("No schedule could be generated yet. Add pets and tasks first.")

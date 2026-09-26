import json
import logging
import os

from models.user import User
from models.project import Project
from models.task import Task

# data/project_data.json, found relative to this file so the CLI works
# no matter which folder you run it from
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "project_data.json")


def clear_all():
    """Empty out every model's list and reset the ID counters."""
    User.all = []
    User.next_id = 1
    Project.all = []
    Project.next_id = 1
    Task.all = []
    Task.next_id = 1


def load_data(filename=DATA_FILE):
    """Load users, projects, and tasks from the JSON file.

    - If the file doesn't exist or is empty, we just start with no data.
    - If the file isn't valid JSON, it gets renamed to .bak (so nothing is
      lost) and we start with no data.
    - Any single record that is broken gets skipped with a warning.
    """
    clear_all()

    try:
        with open(filename, "r") as file:
            contents = file.read()
    except FileNotFoundError:
        logging.debug(f"No data file at {filename}, starting fresh.")
        return

    if not contents.strip():
        logging.debug("Data file is empty, starting fresh.")
        return

    try:
        data = json.loads(contents)
    except json.JSONDecodeError:
        backup = filename + ".bak"
        os.replace(filename, backup)
        print(f"⚠️  {filename} was not valid JSON. It was moved to {backup}.")
        return

    if not isinstance(data, dict):
        print("⚠️  Data file is in the wrong format, starting with no data.")
        return

    # users have to load first, then projects, then tasks,
    # because projects need their user and tasks need their project
    for user_data in data.get("users", []):
        try:
            User.from_dict(user_data)
        except (KeyError, ValueError, TypeError) as error:
            print(f"⚠️  Skipping a bad user record: {error}")

    for project_data in data.get("projects", []):
        try:
            Project.from_dict(project_data)
        except (KeyError, ValueError, TypeError) as error:
            print(f"⚠️  Skipping a bad project record: {error}")

    for task_data in data.get("tasks", []):
        try:
            Task.from_dict(task_data)
        except (KeyError, ValueError, TypeError) as error:
            print(f"⚠️  Skipping a bad task record: {error}")

    logging.debug(
        f"Loaded {len(User.all)} users, {len(Project.all)} projects, "
        f"{len(Task.all)} tasks from {filename}"
    )


def save_data(filename=DATA_FILE):
    """Save every user, project, and task to the JSON file."""
    data = {
        "users": [user.to_dict() for user in User.all],
        "projects": [project.to_dict() for project in Project.all],
        "tasks": [task.to_dict() for task in Task.all],
    }

    # make sure the data folder exists before writing
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

    logging.debug(f"Saved data to {filename}")

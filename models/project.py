from datetime import datetime

from models.user import User


class Project:
    """A project that belongs to one user. One project can have many tasks."""

    # Class attributes
    all = []
    next_id = 1

    def __init__(self, title, user, description="", due_date="", id=None):
        """Create a project, give it an ID, and add it to Project.all.

        The id argument is only used when loading projects from the JSON file.
        """
        self.title = title
        self.user = user
        self.description = description
        self.due_date = due_date

        if id is None:
            id = Project.next_id
        self.id = id

        # keep the counter ahead of the biggest id we've seen
        if id >= Project.next_id:
            Project.next_id = id + 1

        Project.all.append(self)

    # Title property
    @property
    def title(self):
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value):
        """Make sure the title is a string that isn't blank."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Project title must be a non-empty string.")
        self._title = value.strip()

    # User property
    @property
    def user(self):
        """Return the User who owns this project."""
        return self._user

    @user.setter
    def user(self, value):
        """The owner has to be a User object."""
        if not isinstance(value, User):
            raise ValueError("A project's owner must be a User.")
        self._user = value

    # Description property
    @property
    def description(self):
        """Return the project description."""
        return self._description

    @description.setter
    def description(self, value):
        """Description is optional, so None just becomes an empty string."""
        if value is None:
            value = ""
        self._description = str(value).strip()

    # Due date property
    @property
    def due_date(self):
        """Return the due date as a 'YYYY-MM-DD' string ("" if there isn't one)."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        """Due date is optional, but if one is given it must be YYYY-MM-DD."""
        if value is None or value == "":
            self._due_date = ""
            return
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(f"Due date must look like YYYY-MM-DD (got '{value}').")
        self._due_date = value

    def tasks(self):
        """Return a list of all the tasks in this project."""
        # imported here to avoid a circular import (task.py imports Project)
        from models.task import Task

        my_tasks = []
        for task in Task.all:
            if task.project == self:
                my_tasks.append(task)
        return my_tasks

    def add_task(self, title, assigned_to="", status="todo"):
        """Create a new task in this project and return it."""
        from models.task import Task

        return Task(title, self, status, assigned_to)

    def task_counts(self):
        """Count how many tasks are in each status, e.g. {"todo": 2, "done": 1}."""
        from models.task import Task

        counts = {}
        for status in Task.STATUSES:
            counts[status] = 0
        for task in self.tasks():
            counts[task.status] += 1
        return counts

    def percent_complete(self):
        """Return the percent of tasks that are done (0 if there are no tasks)."""
        tasks = self.tasks()
        if len(tasks) == 0:
            return 0
        done = self.task_counts()["done"]
        return round(done / len(tasks) * 100)

    @classmethod
    def find_by_title(cls, title):
        """Find a project by title (not case sensitive). Returns None if not found."""
        for project in cls.all:
            if project.title.lower() == title.strip().lower():
                return project
        return None

    @classmethod
    def find_by_id(cls, id):
        """Find a project by ID. Returns None if not found."""
        for project in cls.all:
            if project.id == id:
                return project
        return None

    def to_dict(self):
        """Turn the project into a dictionary so it can be saved as JSON.

        We save the owner's id instead of the whole User object.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "user_id": self.user.id,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a project from a dictionary that was loaded from JSON."""
        user = User.find_by_id(data["user_id"])
        if user is None:
            raise ValueError(f"no user with id {data['user_id']}")
        return cls(
            data["title"],
            user,
            data.get("description", ""),
            data.get("due_date", ""),
            id=data["id"],
        )

    def __str__(self):
        """Readable version of the project for printing."""
        if self.due_date:
            return f"Project #{self.id}: {self.title} (due {self.due_date})"
        return f"Project #{self.id}: {self.title}"

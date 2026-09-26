from models.project import Project


class Task:
    """A single task inside a project."""

    # Class attributes
    STATUSES = ["todo", "in-progress", "done"]
    all = []
    next_id = 1

    def __init__(self, title, project, status="todo", assigned_to="", id=None):
        """Create a task, give it an ID, and add it to Task.all.

        assigned_to is the name of the user doing the task ("" if nobody).
        The id argument is only used when loading tasks from the JSON file.
        """
        self.title = title
        self.project = project
        self.status = status
        self.assigned_to = assigned_to

        if id is None:
            id = Task.next_id
        self.id = id

        # keep the counter ahead of the biggest id we've seen
        if id >= Task.next_id:
            Task.next_id = id + 1

        Task.all.append(self)

    # Title property
    @property
    def title(self):
        """Return the task title."""
        return self._title

    @title.setter
    def title(self, value):
        """Make sure the title is a string that isn't blank."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task title must be a non-empty string.")
        self._title = value.strip()

    # Project property
    @property
    def project(self):
        """Return the Project this task belongs to."""
        return self._project

    @project.setter
    def project(self, value):
        """A task has to belong to a Project object."""
        if not isinstance(value, Project):
            raise ValueError("A task must belong to a Project.")
        self._project = value

    # Status property
    @property
    def status(self):
        """Return the task status."""
        return self._status

    @status.setter
    def status(self, value):
        """Status has to be one of the values in Task.STATUSES."""
        if value not in Task.STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(Task.STATUSES)} (got '{value}')."
            )
        self._status = value

    # Assigned to property
    @property
    def assigned_to(self):
        """Return the name of the person assigned ("" if nobody)."""
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value):
        """Assigned to is optional, so None just becomes an empty string."""
        if value is None:
            value = ""
        self._assigned_to = str(value).strip()

    def complete(self):
        """Mark the task as done."""
        self.status = "done"

    @classmethod
    def find_by_id(cls, id):
        """Find a task by ID. Returns None if not found."""
        for task in cls.all:
            if task.id == id:
                return task
        return None

    def to_dict(self):
        """Turn the task into a dictionary so it can be saved as JSON.

        We save the project's id instead of the whole Project object.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "project_id": self.project.id,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a task from a dictionary that was loaded from JSON."""
        project = Project.find_by_id(data["project_id"])
        if project is None:
            raise ValueError(f"no project with id {data['project_id']}")
        return cls(
            data["title"],
            project,
            data.get("status", "todo"),
            data.get("assigned_to", ""),
            id=data["id"],
        )

    def __str__(self):
        """Readable version of the task for printing."""
        if self.assigned_to:
            return f"Task #{self.id}: [{self.status}] {self.title} - {self.assigned_to}"
        return f"Task #{self.id}: [{self.status}] {self.title}"

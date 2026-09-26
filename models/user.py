class User:
    """A user of the app. One user can have many projects."""

    # Class attributes
    all = []
    next_id = 1

    def __init__(self, name, email="", id=None):
        """Create a user, give it an ID, and add it to User.all.

        The id argument is only used when loading users from the JSON file.
        """
        self.name = name
        self.email = email

        if id is None:
            id = User.next_id
        self.id = id

        # keep the counter ahead of the biggest id we've seen
        if id >= User.next_id:
            User.next_id = id + 1

        User.all.append(self)

    # Name property
    @property
    def name(self):
        """Return the user's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Make sure the name is a string that isn't blank."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string.")
        self._name = value.strip()

    # Email property
    @property
    def email(self):
        """Return the user's email ("" if they don't have one)."""
        return self._email

    @email.setter
    def email(self, value):
        """Email is optional, but if one is given it needs an @ and a dot."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("Email must be a string.")
        value = value.strip()
        if value != "" and ("@" not in value or "." not in value):
            raise ValueError(f"'{value}' is not a valid email address.")
        self._email = value

    def projects(self):
        """Return a list of all the projects that belong to this user."""
        # imported here to avoid a circular import (project.py imports User)
        from models.project import Project

        my_projects = []
        for project in Project.all:
            if project.user == self:
                my_projects.append(project)
        return my_projects

    def add_project(self, title, description="", due_date=""):
        """Create a new project owned by this user and return it."""
        from models.project import Project

        return Project(title, self, description, due_date)

    @classmethod
    def find_by_name(cls, name):
        """Find a user by name (not case sensitive). Returns None if not found."""
        for user in cls.all:
            if user.name.lower() == name.strip().lower():
                return user
        return None

    @classmethod
    def find_by_id(cls, id):
        """Find a user by ID. Returns None if not found."""
        for user in cls.all:
            if user.id == id:
                return user
        return None

    def to_dict(self):
        """Turn the user into a dictionary so it can be saved as JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a user from a dictionary that was loaded from JSON."""
        return cls(data["name"], data.get("email", ""), id=data["id"])

    def __str__(self):
        """Readable version of the user for printing."""
        if self.email:
            return f"User #{self.id}: {self.name} <{self.email}>"
        return f"User #{self.id}: {self.name}"

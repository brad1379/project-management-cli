from tabulate import tabulate


def format_users(users):
    """Return a table of users as a string."""
    if len(users) == 0:
        return "No users found."

    rows = []
    for user in users:
        rows.append([user.id, user.name, user.email or "-", len(user.projects())])

    return tabulate(rows, headers=["ID", "Name", "Email", "Projects"], tablefmt="grid")


def format_projects(projects):
    """Return a table of projects as a string."""
    if len(projects) == 0:
        return "No projects found."

    rows = []
    for project in projects:
        rows.append(
            [
                project.id,
                project.title,
                project.user.name,
                project.due_date or "-",
                len(project.tasks()),
                f"{project.percent_complete()}%",
            ]
        )

    headers = ["ID", "Title", "Owner", "Due Date", "Tasks", "Done"]
    return tabulate(rows, headers=headers, tablefmt="grid")


def format_tasks(tasks):
    """Return a table of tasks as a string."""
    if len(tasks) == 0:
        return "No tasks found."

    rows = []
    for task in tasks:
        rows.append(
            [task.id, task.title, task.status, task.assigned_to or "-", task.project.title]
        )

    headers = ["ID", "Title", "Status", "Assigned To", "Project"]
    return tabulate(rows, headers=headers, tablefmt="grid")


def format_project_details(project):
    """Return a full description of one project, including its tasks."""
    lines = [
        f"📁 {project.title}",
        f"Owner:       {project.user.name}",
        f"Description: {project.description or '-'}",
        f"Due date:    {project.due_date or '-'}",
        f"Progress:    {project.percent_complete()}% done",
        "",
        format_tasks(project.tasks()),
    ]
    return "\n".join(lines)


def format_summary(project_title, summary):
    """Put a heading above the AI summary so it's easy to read."""
    line = "=" * 50
    return f"\n{line}\n🤖 AI Summary for '{project_title}'\n{line}\n{summary}\n"

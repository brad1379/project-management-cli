import argparse
import logging

from models.user import User
from models.project import Project
from models.task import Task
from services.storage_service import DATA_FILE, load_data, save_data
from services.ai_client import DEFAULT_MODEL, summarize_project
from utils.formatters import (
    format_users,
    format_projects,
    format_tasks,
    format_project_details,
    format_summary,
)


# ---------- helper functions ----------

def get_user(name):
    """Find a user by name, or raise a ValueError with a helpful message."""
    user = User.find_by_name(name)
    if user is None:
        raise ValueError(f"No user named '{name}'. Use list-users to see all users.")
    return user


def get_project(title):
    """Find a project by title, or raise a ValueError with a helpful message."""
    project = Project.find_by_title(title)
    if project is None:
        raise ValueError(
            f"No project titled '{title}'. Use list-projects to see all projects."
        )
    return project


def get_task(id):
    """Find a task by ID, or raise a ValueError with a helpful message."""
    task = Task.find_by_id(id)
    if task is None:
        raise ValueError(f"No task with ID {id}. Use list-tasks to see all tasks.")
    return task


# ---------- user commands ----------

def add_user(args):
    """Create a new user."""
    if User.find_by_name(args.name):
        raise ValueError(f"A user named '{args.name}' already exists.")
    user = User(args.name, args.email)
    save_data(args.data_file)
    print(f"✅ Added {user}")


def list_users(args):
    """Show all users in a table."""
    print(format_users(User.all))


def update_user(args):
    """Change a user's name and/or email."""
    user = get_user(args.name)

    if args.new_name:
        other_user = User.find_by_name(args.new_name)
        if other_user and other_user != user:
            raise ValueError(f"A user named '{args.new_name}' already exists.")
        old_name = user.name
        user.name = args.new_name
        # tasks store the assigned person's name, so update those too
        for task in Task.all:
            if task.assigned_to == old_name:
                task.assigned_to = user.name

    if args.email is not None:
        user.email = args.email

    save_data(args.data_file)
    print(f"✅ Updated {user}")


# ---------- project commands ----------

def add_project(args):
    """Create a new project for a user."""
    user = get_user(args.user)
    if Project.find_by_title(args.title):
        raise ValueError(f"A project titled '{args.title}' already exists.")
    project = user.add_project(args.title, args.description, args.due_date)
    save_data(args.data_file)
    print(f"✅ Added {project} for {user.name}")


def list_projects(args):
    """Show all projects, or just one user's projects if --user is given."""
    if args.user:
        projects = get_user(args.user).projects()
    else:
        projects = Project.all
    print(format_projects(projects))


def view_project(args):
    """Show the details and tasks for one project."""
    project = get_project(args.project)
    print(format_project_details(project))


def update_project(args):
    """Change a project's title, description, due date, or owner."""
    project = get_project(args.project)

    if args.new_title:
        other_project = Project.find_by_title(args.new_title)
        if other_project and other_project != project:
            raise ValueError(f"A project titled '{args.new_title}' already exists.")
        project.title = args.new_title
    if args.description is not None:
        project.description = args.description
    if args.due_date is not None:
        project.due_date = args.due_date
    if args.user:
        project.user = get_user(args.user)

    save_data(args.data_file)
    print(f"✅ Updated {project}")


# ---------- task commands ----------

def add_task(args):
    """Create a new task in a project."""
    project = get_project(args.project)

    assigned_to = ""
    if args.assigned_to:
        assigned_to = get_user(args.assigned_to).name

    task = project.add_task(args.title, assigned_to, args.status)
    save_data(args.data_file)
    print(f"✅ Added {task} to '{project.title}'")


def list_tasks(args):
    """Show all tasks, optionally filtered by project and/or status."""
    if args.project:
        tasks = get_project(args.project).tasks()
    else:
        tasks = Task.all

    if args.status:
        filtered = []
        for task in tasks:
            if task.status == args.status:
                filtered.append(task)
        tasks = filtered

    print(format_tasks(tasks))


def update_task(args):
    """Change a task's title, status, or who it's assigned to."""
    task = get_task(args.id)

    if args.title:
        task.title = args.title
    if args.status:
        task.status = args.status
    if args.assigned_to is not None:
        if args.assigned_to == "":
            task.assigned_to = ""  # un-assign the task
        else:
            task.assigned_to = get_user(args.assigned_to).name

    save_data(args.data_file)
    print(f"✅ Updated {task}")


def complete_task(args):
    """Mark a task as done."""
    task = get_task(args.id)
    task.complete()
    save_data(args.data_file)
    print(f"✅ Completed {task}")


# ---------- AI command ----------

def summarize(args):
    """Ask the AI model for a summary, risks, and next step for a project."""
    project = get_project(args.project)
    print(f"⏳ Asking {args.model} to summarize '{project.title}'...")

    try:
        summary = summarize_project(project, args.model)
    except RuntimeError as error:
        # the AI part failing shouldn't crash the whole app
        print(f"❌ AI service error: {error}")
        return

    print(format_summary(project.title, summary))


# ---------- CLI setup ----------

def build_parser():
    """Set up argparse with all of the subcommands and their options."""
    parser = argparse.ArgumentParser(
        description="Project Management CLI - manage users, projects, and tasks."
    )
    parser.add_argument(
        "--data-file", default=DATA_FILE, help="JSON file to load and save data"
    )
    parser.add_argument(
        "--debug", action="store_true", help="print debug logging to trace what's happening"
    )
    subparsers = parser.add_subparsers()

    # add-user
    add_user_parser = subparsers.add_parser("add-user", help="Add a new user")
    add_user_parser.add_argument("--name", required=True)
    add_user_parser.add_argument("--email", default="")
    add_user_parser.set_defaults(func=add_user)

    # list-users
    list_users_parser = subparsers.add_parser("list-users", help="List all users")
    list_users_parser.set_defaults(func=list_users)

    # update-user
    update_user_parser = subparsers.add_parser("update-user", help="Update a user")
    update_user_parser.add_argument("--name", required=True, help="current name")
    update_user_parser.add_argument("--new-name")
    update_user_parser.add_argument("--email")
    update_user_parser.set_defaults(func=update_user)

    # add-project
    add_project_parser = subparsers.add_parser("add-project", help="Add a project for a user")
    add_project_parser.add_argument("--user", required=True)
    add_project_parser.add_argument("--title", required=True)
    add_project_parser.add_argument("--description", default="")
    add_project_parser.add_argument("--due-date", default="", help="YYYY-MM-DD")
    add_project_parser.set_defaults(func=add_project)

    # list-projects
    list_projects_parser = subparsers.add_parser("list-projects", help="List projects")
    list_projects_parser.add_argument("--user", help="only show this user's projects")
    list_projects_parser.set_defaults(func=list_projects)

    # view-project
    view_project_parser = subparsers.add_parser("view-project", help="Show one project and its tasks")
    view_project_parser.add_argument("--project", required=True)
    view_project_parser.set_defaults(func=view_project)

    # update-project
    update_project_parser = subparsers.add_parser("update-project", help="Update a project")
    update_project_parser.add_argument("--project", required=True, help="current title")
    update_project_parser.add_argument("--new-title")
    update_project_parser.add_argument("--description")
    update_project_parser.add_argument("--due-date", help="YYYY-MM-DD")
    update_project_parser.add_argument("--user", help="give the project to another user")
    update_project_parser.set_defaults(func=update_project)

    # add-task
    add_task_parser = subparsers.add_parser("add-task", help="Add a task to a project")
    add_task_parser.add_argument("--project", required=True)
    add_task_parser.add_argument("--title", required=True)
    add_task_parser.add_argument("--assigned-to", help="name of an existing user")
    add_task_parser.add_argument("--status", default="todo", choices=Task.STATUSES)
    add_task_parser.set_defaults(func=add_task)

    # list-tasks
    list_tasks_parser = subparsers.add_parser("list-tasks", help="List tasks")
    list_tasks_parser.add_argument("--project", help="only show this project's tasks")
    list_tasks_parser.add_argument("--status", choices=Task.STATUSES)
    list_tasks_parser.set_defaults(func=list_tasks)

    # update-task
    update_task_parser = subparsers.add_parser("update-task", help="Update a task")
    update_task_parser.add_argument("--id", type=int, required=True)
    update_task_parser.add_argument("--title")
    update_task_parser.add_argument("--status", choices=Task.STATUSES)
    update_task_parser.add_argument("--assigned-to", help='user name, or "" to un-assign')
    update_task_parser.set_defaults(func=update_task)

    # complete-task
    complete_task_parser = subparsers.add_parser("complete-task", help="Mark a task as done")
    complete_task_parser.add_argument("--id", type=int, required=True)
    complete_task_parser.set_defaults(func=complete_task)

    # summarize-project
    summarize_parser = subparsers.add_parser(
        "summarize-project", help="Get an AI summary and next step for a project"
    )
    summarize_parser.add_argument("--project", required=True)
    summarize_parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    summarize_parser.set_defaults(func=summarize)

    return parser


def main():
    """CLI entry point: parse the command, load data, and run the command."""
    parser = build_parser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="[debug] %(message)s")

    if not hasattr(args, "func"):
        parser.print_help()
        return

    load_data(args.data_file)

    try:
        args.func(args)
    except ValueError as error:
        print(f"❌ {error}")


if __name__ == "__main__":
    main()

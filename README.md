# Project Management CLI

A command-line tool for managing users, projects, and tasks. Admins can add, view, and update users, projects, and tasks, and everything is saved to a JSON file. The tool can also ask a local AI model (through [Ollama](https://ollama.com)) for a quick summary, risk notes, and a suggested next step for any project.

## Setup

### Requirements

- Python 3.12
- [Ollama](https://ollama.com/download), only needed for the `summarize-project` command

### Install dependencies

With pipenv:

```bash
pipenv install
pipenv shell
```

Or with pip:

```bash
pip install -r requirements.txt
```

### Set up Ollama (for the AI feature)

1. Download and install Ollama from https://ollama.com/download
2. Download the model:
   ```bash
   ollama pull llama3.2
   ```
3. Make sure Ollama is running (it usually starts on its own after installing; if not, run `ollama serve`).

Every other command works without Ollama.

## How to Run

Run commands from the project folder:

```bash
python main.py <command> [options]
```

To see all commands:

```bash
python main.py --help
```

To see the options for one command:

```bash
python main.py add-task --help
```

### Global options

| Option | What it does |
| --- | --- |
| `--data-file PATH` | Use a different JSON file (handy for testing with mock data) |
| `--debug` | Print debug messages to trace what the program is doing |

Global options go **before** the command, for example: `python main.py --debug list-users`

## Example Commands

```bash
# Users
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py list-users
python main.py update-user --name "Alex" --new-name "Alexander" --email "alex@new.com"

# Projects
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a project manager" --due-date 2026-10-15
python main.py list-projects
python main.py list-projects --user "Alex"
python main.py view-project --project "CLI Tool"
python main.py update-project --project "CLI Tool" --due-date 2026-11-01

# Tasks
python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex"
python main.py list-tasks
python main.py list-tasks --project "CLI Tool" --status todo
python main.py update-task --id 1 --status in-progress
python main.py complete-task --id 1

# AI summary
python main.py summarize-project --project "CLI Tool"
python main.py summarize-project --project "CLI Tool" --model llama3.2
```

### Example output

```
$ python main.py list-projects
+------+----------+---------+------------+---------+--------+
|   ID | Title    | Owner   | Due Date   |   Tasks | Done   |
+======+==========+=========+============+=========+========+
|    1 | CLI Tool | Alex    | 2026-11-01 |       3 | 33%    |
+------+----------+---------+------------+---------+--------+
```

## All Commands

| Command | Required options | Optional options |
| --- | --- | --- |
| `add-user` | `--name` | `--email` |
| `list-users` | | |
| `update-user` | `--name` | `--new-name`, `--email` |
| `add-project` | `--user`, `--title` | `--description`, `--due-date` |
| `list-projects` | | `--user` |
| `view-project` | `--project` | |
| `update-project` | `--project` | `--new-title`, `--description`, `--due-date`, `--user` |
| `add-task` | `--project`, `--title` | `--assigned-to`, `--status` |
| `list-tasks` | | `--project`, `--status` |
| `update-task` | `--id` | `--title`, `--status`, `--assigned-to` |
| `complete-task` | `--id` | |
| `summarize-project` | `--project` | `--model` |

Task statuses are `todo`, `in-progress`, and `done`. Due dates use the format `YYYY-MM-DD`.

## File Structure

```
project-management-cli/
├── main.py                     # CLI entry point: argparse setup and command functions
├── models/
│   ├── user.py                 # User class (name, email)
│   ├── project.py              # Project class (title, description, due_date)
│   └── task.py                 # Task class (title, status, assigned_to)
├── services/
│   ├── storage_service.py      # Loads and saves everything to the JSON file
│   └── ai_client.py            # Sends project data to Ollama and returns a summary
├── data/
│   └── project_data.json       # Where users, projects, and tasks are saved
├── utils/
│   └── formatters.py           # Turns users/projects/tasks into tables for printing
├── Pipfile / Pipfile.lock      # pipenv dependencies
├── requirements.txt            # pip dependencies
└── README.md
```

## Features

- **Users, projects, and tasks.** Add, view, and update all three from the command line.
- **Relationships.** One user has many projects (`user.projects()`), and one project has many tasks (`project.tasks()`).
- **Validation.** Properties with setters reject bad data, like blank names, invalid emails, badly formatted due dates, or unknown statuses, and show a clear error message.
- **Auto IDs.** Each class uses a class attribute (`next_id`) to give every new object a unique ID.
- **JSON saving.** Data is saved to `data/project_data.json` after every change and loaded at startup.
- **Error handling.** Missing, empty, or broken data files don't crash the app (see "Known issues" below).
- **Readable output.** Tables are built with the `tabulate` package.
- **Progress tracking.** Each project shows how many tasks it has and what percent are done.
- **AI project summary.** See the next section.

## AI Feature: `summarize-project`

The `summarize-project` command sends a project's details to a local AI model and prints back:

- **Summary:** where the project stands
- **Risks:** anything that could cause problems (like unassigned or unfinished tasks)
- **Next Step:** one thing the team should do next

### How it works

All of the AI code lives in `services/ai_client.py`, so `main.py` never talks to Ollama directly.

1. `build_project_data(project)` collects the project and its tasks into a dictionary (title, owner, due date, percent complete, task counts, and every task).
2. `build_summary_prompt(project)` turns that dictionary into JSON and puts it inside a prompt that asks for the three sections.
3. `send_prompt(prompt)` sends the prompt to Ollama using `ollama.chat` and returns the reply. This function is reusable because it doesn't know anything about projects.
4. `summarize_project(project)` ties the steps together.

If Ollama isn't running, or the model isn't downloaded, `send_prompt` raises a `RuntimeError`. The CLI catches it and prints a message instead of crashing:

```
❌ AI service error: Could not get a response from Ollama (...). Make sure Ollama is running and the 'llama3.2' model is downloaded (ollama pull llama3.2).
```

The default model is `llama3.2`. You can use a different one with `--model`.

## Known Issues and Limitations

- **Names and titles must be unique.** Users are looked up by name and projects by title (not case sensitive), so two users can't share a name and two projects can't share a title. Tasks are looked up by ID instead.
- **Nothing can be deleted.** There are no commands to delete a user, project, or task yet.
- **Tasks store the assigned user's name**, not their ID. Renaming a user with `update-user` updates their tasks too, but editing the JSON file by hand can get them out of sync.
- **Broken data files.** If `project_data.json` isn't valid JSON, it gets renamed to `project_data.json.bak` and the app starts with empty data. Any single record that's broken (like a project whose user doesn't exist) is skipped with a warning.
- **AI summaries aren't perfect.** The model runs locally and can be slow the first time, and it may sometimes get details wrong or not follow the exact format.
- **One admin at a time.** There are no logins or permissions; anyone who can run the CLI can change the data.

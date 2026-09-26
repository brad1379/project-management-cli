import json
import logging

import ollama

DEFAULT_MODEL = "llama3.2"


def send_prompt(prompt, model_name=DEFAULT_MODEL):
    """Send a prompt to the local Ollama model and return its reply as a string.

    This function doesn't know anything about projects - it just sends text
    and gets text back, so it can be reused for other AI features.

    Raises ValueError for an empty prompt and RuntimeError if the service
    can't be reached or sends back an empty answer.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    logging.debug(f"Sending prompt to {model_name}:\n{prompt}")

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt.strip()}],
        )
        content = response["message"]["content"]
    except Exception as error:
        raise RuntimeError(
            f"Could not get a response from Ollama ({error}). "
            f"Make sure Ollama is running and the '{model_name}' model "
            f"is downloaded (ollama pull {model_name})."
        )

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The AI service sent back an empty response.")

    return content.strip()


def build_project_data(project):
    """Collect a project and its tasks into a plain dictionary."""
    tasks = []
    for task in project.tasks():
        tasks.append(
            {
                "title": task.title,
                "status": task.status,
                "assigned_to": task.assigned_to or "Unassigned",
            }
        )

    return {
        "title": project.title,
        "owner": project.user.name,
        "description": project.description or "None given",
        "due_date": project.due_date or "None given",
        "percent_complete": project.percent_complete(),
        "task_counts": project.task_counts(),
        "tasks": tasks,
    }


def build_summary_prompt(project):
    """Build the prompt text for a project summary, with the data as JSON."""
    project_json = json.dumps(build_project_data(project), indent=2)

    return (
        "You are a helpful project manager assistant.\n"
        "Read the project data below and reply with these three sections:\n"
        "Summary: 2-3 sentences about where the project stands.\n"
        "Risks: any risks you notice (overdue work, unassigned tasks, etc.).\n"
        "Next Step: one specific thing the team should do next.\n\n"
        "Only use the information in the data. Do not make up tasks or people.\n\n"
        f"Project data:\n{project_json}"
    )


def summarize_project(project, model_name=DEFAULT_MODEL):
    """Send a project to the AI model and return a readable summary string."""
    prompt = build_summary_prompt(project)
    return send_prompt(prompt, model_name)

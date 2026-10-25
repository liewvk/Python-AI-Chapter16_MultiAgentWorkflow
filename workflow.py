"""Task queue and supervised multi-agent workflow."""
from uuid import uuid4
from settings import MAX_QUEUE, MAX_TASK_LENGTH, OUTPUT_DIR
from agents import (KnowledgeAgent, LanguageAgent, PLANNER_ROLE,
                    WRITER_ROLE, REVIEWER_ROLE)


class Workflow:
    def __init__(self, language_agent=None, knowledge_agent=None,
                 output_dir=OUTPUT_DIR):
        self.llm = language_agent or LanguageAgent()
        self.knowledge = knowledge_agent or KnowledgeAgent()
        self.output_dir = output_dir
        self.tasks = []

    def add(self, request):
        request = request.strip()
        if not 5 <= len(request) <= MAX_TASK_LENGTH:
            raise ValueError("Enter a request of 5-400 characters.")
        if len(self.tasks) >= MAX_QUEUE:
            raise ValueError("The task queue is full (10 tasks).")
        task = {"id": uuid4().hex[:8], "request": request,
                "status": "queued", "plan": "", "facts": "",
                "draft": "", "review": "", "file": ""}
        self.tasks.append(task)
        return task

    def get(self, identifier):
        for task in self.tasks:
            if task["id"] == identifier:
                return task
        raise ValueError("Task ID not found. Use /queue to list tasks.")

    def run_next(self):
        task = next((t for t in self.tasks if t["status"] == "queued"), None)
        if task is None:
            raise ValueError("There are no queued tasks.")
        task["status"] = "running"
        try:
            task["plan"] = self.llm.respond(PLANNER_ROLE, task["request"])
            selected = self.knowledge.retrieve(task["request"])
            facts = "\n".join(
                f"- {item['topic']}: {item['text']}" for item in selected
            ) or "No matching reference information available."
            task["facts"] = facts
            task["draft"] = self.llm.respond(
                WRITER_ROLE,
                f"TASK:\n{task['request']}\n\nPLAN:\n{task['plan']}"
                f"\n\nAPPROVED REFERENCE FACTS:\n{facts}",
            )
            task["review"] = self.llm.respond(
                REVIEWER_ROLE,
                f"REQUEST:\n{task['request']}\n\nREFERENCE FACTS:\n{facts}"
                f"\n\nDRAFT:\n{task['draft']}",
            )
            task["status"] = "ready"
            return task
        except Exception:
            task["status"] = "failed"
            raise

    def approve_and_save(self, identifier):
        task = self.get(identifier)
        if task["status"] != "ready":
            raise ValueError("Only a reviewed draft can be saved.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"draft_{task['id']}.txt"
        path.write_text(task["draft"] + "\n", encoding="utf-8")
        task["status"] = "saved"
        task["file"] = str(path)
        return path

    def discard(self, identifier):
        task = self.get(identifier)
        if task["status"] == "saved":
            raise ValueError("A saved file cannot be discarded by this command.")
        task["status"] = "discarded"

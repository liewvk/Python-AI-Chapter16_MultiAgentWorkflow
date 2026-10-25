"""Offline tests: no Ollama model or network required."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents import KnowledgeAgent, LanguageAgent, PLANNER_ROLE
from workflow import Workflow


class FakeClient:
    def __init__(self):
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        role = kwargs["messages"][0]["content"]
        if "PLANNER agent" in role:
            text = "1. Check policy. 2. Draft response."
        elif "WRITER agent" in role:
            text = "DRAFT: Please provide your order number for review."
        else:
            text = "REVIEW: The draft requires human approval."
        return SimpleNamespace(message=SimpleNamespace(content=text))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.client = FakeClient()
        self.flow = Workflow(language_agent=LanguageAgent(self.client),
                             output_dir=Path(self.temp.name) / "output")

    def test_knowledge_retrieves_refund(self):
        found = KnowledgeAgent().retrieve("Explain the refund policy")
        self.assertIn("Refund", found[0]["topic"])

    def test_unrelated_knowledge_is_empty(self):
        self.assertEqual(KnowledgeAgent().retrieve("xyzzy galactic purple"), [])

    def test_add_and_queue(self):
        self.assertEqual(self.flow.add("Prepare a refund reply")["status"], "queued")
        self.assertEqual(len(self.flow.tasks), 1)

    def test_short_request_rejected(self):
        with self.assertRaises(ValueError):
            self.flow.add("hi")

    def test_queue_limit(self):
        for index in range(10):
            self.flow.add(f"Task number {index}")
        with self.assertRaises(ValueError):
            self.flow.add("Another task")

    def test_run_invokes_three_specialized_roles(self):
        task = self.flow.add("Write a refund policy reply")
        result = self.flow.run_next()
        self.assertEqual(result["id"], task["id"])
        self.assertEqual(result["status"], "ready")
        self.assertEqual(len(self.client.calls), 3)
        self.assertEqual(self.client.calls[0]["messages"][0]["content"], PLANNER_ROLE)
        self.assertIn("Refund policy", result["facts"])
        self.assertIn("human approval", result["review"])

    def test_approve_requires_ready(self):
        task = self.flow.add("Write a refund policy reply")
        with self.assertRaises(ValueError):
            self.flow.approve_and_save(task["id"])

    def test_approve_saves_only_draft(self):
        task = self.flow.add("Write a refund policy reply")
        self.flow.run_next()
        path = self.flow.approve_and_save(task["id"])
        self.assertEqual(path.parent, self.flow.output_dir)
        self.assertIn("DRAFT:", path.read_text(encoding="utf-8"))
        self.assertEqual(task["status"], "saved")

    def test_discard_blocks_save(self):
        task = self.flow.add("Write a refund policy reply")
        self.flow.run_next()
        self.flow.discard(task["id"])
        with self.assertRaises(ValueError):
            self.flow.approve_and_save(task["id"])

    def test_empty_model_reply_is_error(self):
        class EmptyClient:
            def chat(self, **kwargs):
                return SimpleNamespace(message=SimpleNamespace(content="  "))
        with self.assertRaises(ValueError):
            LanguageAgent(EmptyClient()).respond(PLANNER_ROLE, "test")

    def test_no_queued_task_raises(self):
        with self.assertRaises(ValueError):
            self.flow.run_next()


if __name__ == "__main__":
    unittest.main()

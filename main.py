"""Interactive console interface for Chapter 16."""
from workflow import Workflow
from settings import MODEL


def help_menu():
    print("\n/add request     Queue a task")
    print("/queue           Show tasks")
    print("/run             Process the next queued task")
    print("/preview ID      View the plan, draft, and review")
    print("/approve ID      Save a draft after human confirmation")
    print("/discard ID      Discard a draft")
    print("/help            Show commands")
    print("/exit            Exit")


def preview(task):
    print("\nTASK:", task["request"])
    print("\nPLAN:\n", task["plan"])
    print("\nREFERENCES:\n", task["facts"])
    print("\nDRAFT:\n", task["draft"])
    print("\nREVIEW:\n", task["review"])
    print("\nStatus:", task["status"])


def main():
    print("CHAPTER 16 - MULTI-AGENT WORKFLOW")
    print("Ollama model:", MODEL)
    flow = Workflow()
    help_menu()
    while True:
        try:
            line = input("\nCommand: ").strip()
            action, _, argument = line.partition(" ")
            action, argument = action.lower(), argument.strip()
            if action == "/exit":
                print("Goodbye!")
                break
            elif action == "/help":
                help_menu()
            elif action == "/add":
                task = flow.add(argument)
                print("Queued:", task["id"])
            elif action == "/queue":
                for task in flow.tasks:
                    print(task["id"], task["status"], task["request"])
                if not flow.tasks:
                    print("The queue is empty.")
            elif action == "/run":
                print("Running Planner > Knowledge > Writer > Reviewer...")
                preview(flow.run_next())
                print("Review carefully before using /approve ID.")
            elif action == "/preview":
                preview(flow.get(argument))
            elif action == "/approve":
                if flow.get(argument)["status"] != "ready":
                    raise ValueError("Run and review this task first.")
                if input("Type SAVE to confirm: ").strip() == "SAVE":
                    print("Saved to:", flow.approve_and_save(argument))
                else:
                    print("Canceled. Nothing saved.")
            elif action == "/discard":
                flow.discard(argument)
                print("Task discarded.")
            elif line:
                print("Unknown command. Type /help.")
        except (ValueError, OSError, ConnectionError, TimeoutError) as error:
            print("Operation failed:", error)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as error:
            print("AI operation failed:", error)


if __name__ == "__main__":
    main()

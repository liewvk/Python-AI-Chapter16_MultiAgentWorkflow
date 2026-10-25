# Chapter 16 — Multi-Agent Workflows and Task Automation

This example accompanies *Python AI Agents Made Easy*, Chapter 16. It uses the local Ollama `qwen3.5:9b` model in three role-specialized calls: Planner, Writer, Reviewer. A deterministic Knowledge Agent retrieves relevant fictional office policy notes. A Python task queue coordinates these stages. **Nothing is emailed, transmitted to a customer, or scheduled in the background.** The user explicitly approves any draft saved to disk.

## Start in Visual Studio 2026

1. Extract this ZIP to a writable folder. Open `Chapter16_MultiAgentWorkflow.sln` using **Open a project or solution**, **not** Open Folder.
2. Open Developer PowerShell **in the extracted folder containing `requirements.txt`**.
3. Run:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ollama pull qwen3.5:9b
   ```

4. In Solution Explorer, ensure your active interpreter is `.venv\Scripts\python.exe`. If needed, open project Properties > Debug and set **Interpreter Path** to that exact file.
5. Ensure `main.py` is the startup file. Press **Ctrl+F5**.

Ollama needs to be running. If your computer only supports a smaller model, pull `qwen3.5:4b` and change `MODEL` in `settings.py`.

## Commands

- `/add Draft a refund policy response to a customer` — queue a task
- `/add Write a friendly password reset guide for staff` — queue another
- `/queue` — list task IDs and statuses
- `/run` — run the next task through Planner → Knowledge → Writer → Reviewer
- `/preview ID` — inspect the model outputs
- `/approve ID` — explicitly confirm with `SAVE` to write `output/draft_ID.txt`
- `/discard ID` — discard an unsaved task
- `/help` and `/exit`

The `data/office_policies.json` file contains **fictional BrightDesk** facts for demonstration. The system does not contain sensitive personal data or real policies.

## Offline testing

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests use a simulated local-model client; they do not require Ollama or an installed AI model. Live Qwen inference is not verified by the offline tests.

## Scope and limitations

- All steps run synchronously when the user types `/run`; this is **workflow automation**, not timed/background scheduling.
- The three language agents are role-specific prompts sent to the **same Qwen model**, not separate AI models or independently running processes.
- Policy retrieval uses simple word matching; unsupported information must be verified by a person.
- Model-generated reviewer feedback is advisory. Human approval remains mandatory.
- The queue exists only while this process runs. Saved draft files persist; queued tasks do not.
- The model output is never executed as code, and no external messages are sent.

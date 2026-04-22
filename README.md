# Auto-Skill Core

Auto-Skill is a framework designed to empower AI Coding Assistants (like Antigravity, Cursor, or Claude Code) with a "Second Brain". It uses a dynamic experience-distillation loop to help the AI learn from its own successes and failures.

## 🚀 Key Features

*   **Real-time Learning**: Distills specific technical "lessons learned" into reusable rules.
*   **Context Injection**: Automatically prepares the perfect environment context for every task.
*   **Global Shielding**: Automatically reinforces your IDE's global rules to ensure the Auto-Skill protocol is never forgotten.
*   **Privacy First**: Separates the core engine from your private "vault" (experiences, diaries, DNA).

## 🛠️ Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/your-username/auto-skill-core.git
    ```
2.  Setup your configuration:
    -   Copy `auto-skill.config.example.json` to `auto-skill.config.json`.
    -   Update the paths appropriate for your Operating System.
3.  Inject the Startup Protocol:
    ```bash
    python scripts/global_reinforce.py
    ```

## 🧠 How it Works

The system operates via two primary protocols:
- **SKILL.md**: Tasks Pre-flight protocol.
- **SKILL_CLOSE.md**: Tasks Debrief & Distillation protocol.

---

## 📜 Credits

This project is a refactored and generalized version of the original framework created by **[Toolsai/auto-skill](https://github.com/Toolsai/auto-skill)**. Special thanks to the original author for the concept of the distillation loop.

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.

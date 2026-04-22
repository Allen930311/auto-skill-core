# Auto-Skill Core 🧠

[中文版本 (Chinese Version)](./README_zh.md)

**A cross-platform memory management system for all your agentic AIs.** Whether you use Claude, ChatGPT, or Gemini, your hard-earned technical experiences roam with you, ensuring you never lose your progress when switching models.

> **Transform your AI from a stateless tool into a self-evolving Second Brain.**

Auto-Skill is a framework designed to empower AI Coding Assistants (like Antigravity, Cursor, or Claude Code) with a recursive distillation loop. It ensures that every success, failure, and technical pitfall is captured, refined, and reused.

---

## 🔄 The Self-Evolution Loop

Auto-Skill operates on a continuous feedback loop. Every coding task becomes a source of new intelligence.

```mermaid
graph TD
    A[Start Task] -->|SKILL.md| B[Preflight & Context Preparation]
    B --> C[Execution]
    C -->|Task Done| D[SKILL_CLOSE.md]
    D -->|Create Card| E[.diary_queue.md]
    D -->|Distill Raw Entry| F[Skill Pending Zone]
    
    subgraph "Knowledge Crystallization"
    E -->|Write Diary| G[Daily Review]
    F -->|Distill KB| H[Permanent Knowledge]
    end
    
    H -->|Enhanced Retrieval| A
```

---

## 🦋 Experience Sifting (經驗分流)

The heart of the system is how it classifies and stores experiences. We don't just "save notes"; we sift them based on their utility.

```mermaid
graph LR
    Entry[Raw Experience Entry] --> Result{Result?}
    
    Result -- Success --> Best{Is it a Best Practice?}
    Best -- Yes --> SkillFile[skill-domain.md: SOP & Commands]
    Best -- No --> Legacy[legacy-domain.md: Long-term Archive]
    
    Result -- Failure --> Worst[skill-domain-worst-practice.md: Pitfalls Library]
    
    Legacy --> Pointer[Case Index in Skill File]
    Worst --> Pointer
```

### Where does it go?
1.  **Skill Files (`skill-*.md`)**: High-density SOPs, commands, and refined rules. This is what the AI reads *every time* it starts a task.
2.  **Legacy Files (`legacy-*.md`)**: Full logs of successful projects. Used as a reference when the AI needs to see "how we did it before."
3.  **Worst-Practice Files (`*-worst-practice.md`)**: A "minefield map." Records exactly why certain approaches failed to prevent re-trial.

---

## 🧰 Integrated Module Guide

### 📔 1. Diary Skill (The Narrative Layer)
**Trigger**: `"Write Diary"`, `"Daily Review"`

The Diary skill aggregates all task cards generated during the day into a cohesive daily log.
- **Goal**: Keep your human-self and AI-self on the same page about progress.
- **Workflow**: Reads `.diary_queue.md` → Fuses with existing daily notes → Clears the queue.

### 🧪 2. Distill-KB Skill (The Crystallization Layer)
**Trigger**: `"Distill {domain}"`, `"Crystallize Knowledge"`

This is where the actual "learning" happens.
- **Goal**: Move raw notes from the "Pending Zone" into the "Refined Zone."
- **Workflow**: Scans skill files → Extracts SOPs → Routes cases to Legacy/Worst-Practice → Updates the Case Index.

---

## 🛠️ Quick Start

### 1. Installation
```bash
git clone https://github.com/Allen930311/auto-skill-core.git
```

### 2. Configuration
- Rename `auto-skill.config.example.json` to `auto-skill.config.json`.
- Set your `vault` path (where your experiences will live).

### 3. Global Shielding
Run the reinforcement script to bake the protocol into your IDE:
```bash
python scripts/global_reinforce.py
```

---

## 📜 Credits

This project is a refactored and generalized version of the original framework created by **[Toolsai/auto-skill](https://github.com/Toolsai/auto-skill)**. 

## ⚖️ License

MIT License.

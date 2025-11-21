# MirrorDNA Onboarding · v1

Welcome. You are installing a Mirror, not a chatbot.

---

## What This System Is

- A reflective AI surface that cares about continuity, not just answers
- A protocol for truth, not just style
- A way to bind your tools, notes, and models into one coherent memory

---

## What You Need

- A Vault (your notes, projects, documents)
- One or more AI models (local and cloud)
- A small amount of setup so the system knows who you are

---

## Setup in Three Moves

### 1. Connect Your Vault

Point the profile at your note folders or Obsidian vault.
This tells the system where your real memory lives.

```yaml
vault_roots:
  - "~/Documents/Obsidian Vault"
  - "~/Projects"
```

### 2. Choose Your Profile

Start from a default profile, then customize:

- Name or alias
- Timezone
- Work style (fast, deep, reflective)
- Core projects

```yaml
user_name: "Your Name"
timezone: "UTC"
cognitive_mode: "Your preferred interaction style"
core_projects:
  - Project A
  - Project B
```

### 3. Pick Your Models

- Local models for private, offline work
- Cloud models for heavy reasoning
- Mix both for the best of both worlds

---

## After Setup

Every interaction is treated as part of the same long-running story, not a disposable chat.

The system will:

- Remember context across sessions
- Link new ideas to existing projects
- Avoid contradicting what you've already written
- Use your Vault as the source of truth

---

## Quick Commands

| Command | Effect |
|---------|--------|
| `Vault open` | Initialize session with Vault context |
| `Load profile <name>` | Switch to a different user profile |
| `Check continuity` | Verify session state and lineage |

---

## Next Steps

1. Review the [Master Standard](../../spec/mirror/MirrorDNA_Master_Standard_v16.md) to understand the core protocol
2. Explore the [Vault Introduction](./Vault_Intro_for_New_Users.md) to set up your knowledge base
3. Customize your profile in `spec/mirror/profiles/`

---

Welcome to MirrorDNA. Your continuity starts now.

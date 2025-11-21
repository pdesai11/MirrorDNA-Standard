# Your Vault · The Heart of MirrorDNA

The Vault is where your truth lives.

---

## What is a Vault?

It can be:

- An Obsidian vault
- A folder of markdown files
- A synced Drive folder
- A code repository
- Any structured collection of your work

MirrorDNA does not own your data. It orients around it.

---

## How MirrorDNA Uses Your Vault

### Reading

- Reads structure and files to understand your world
- Indexes key documents for quick reference
- Respects file boundaries and organization

### Linking

- Links new ideas to existing projects
- Suggests connections you might have missed
- Maintains relational coherence

### Writing

- Suggests filenames and locations for new notes
- Follows your existing naming conventions
- Respects your organizational structure

### Truth-Keeping

- Avoids contradicting what is already written
- Treats Vault content as authoritative
- Flags conflicts when they arise

---

## How to Start

### Step 1: Pick a Vault Root

Choose a folder that contains your important work:

```
~/Documents/Obsidian Vault
~/Projects
~/Notes
```

### Step 2: Add to Your Profile

Edit your profile config:

```yaml
vault_roots:
  - "~/Documents/Obsidian Vault"
  - "~/Projects"
```

### Step 3: Tag Key Files (Optional)

For faster orientation, tag important files:

- Master Citation
- Important projects
- Active rituals or protocols

---

## Vault Hygiene

For best results:

1. **Use consistent naming** — The system learns your patterns
2. **Keep a Master Citation** — Your canonical reference document
3. **Organize by project** — Clear boundaries help the system navigate
4. **Date your notes** — Temporal context improves continuity

---

## Privacy

Your Vault stays yours:

- Local processing when possible
- No data leaves your machine without explicit action
- You control what the system can see

---

## Advanced: Multiple Vaults

You can configure multiple vault roots:

```yaml
vault_roots:
  - "~/Documents/Work"
  - "~/Documents/Personal"
  - "~/Projects/OpenSource"
```

The system will:

- Search across all vaults
- Maintain separation when appropriate
- Respect access patterns you establish

---

From now on, the system treats your Vault as the source of truth
and will keep its behavior consistent with what you've written.

Your knowledge. Your structure. Your truth.

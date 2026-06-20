# Claude Second-Brain & AI Memory: Complete Reference (2026)

**Source:** Live queries to the *Claude - Complete Guide 2026 (NexusPoint)* NotebookLM notebook (`63a3705e-e871-4830-83a5-966f584a3142`) against new YouTube sources on second-brain/memory setups. Queried 2026-06-20. Treat as **practitioner consensus, not Anthropic documentation** - tool names, level frameworks, and specific commands are creator opinion and move fast.

---

## What is a Claude Second-Brain?

A Claude second-brain (also called an AI OS or AI Operating System) is a **highly personalized, always-on AI infrastructure** that acts as a continuous repository of your knowledge, business operations, and preferences. Instead of a tool you query, it functions as a digital co-founder or executive assistant that knows what is going on in your world better than you do - instantly recalling meeting notes, strategies, relationships, and decisions.

**How it differs from regular AI chat:**
- Regular chat = stateless, disposable threads. Every new conversation starts blank. You re-explain brand voice, project history, and context every time.
- Second-brain = Claude linked to a structured local file system (or vector database) that it can read, write, and maintain. It remembers previous decisions, learns how you work, and pulls in exactly the context it needs without polluting the chat window.
- Token cost: querying a pre-built wiki uses up to 95% fewer tokens than re-reading raw transcripts each time.

**The four-word principle (Four C's framework):** Context, Connections, Capabilities, Cadence.

---

## The 5 Levels of an AI Second-Brain

Mapped by creators **Nate Herk** (5 Levels of an AI Second Brain) and **Chase AI** (7 Levels of Claude Code & RAG). Same escalation pattern:

### Level 1 - Exact Match Retrieval & Basic Routing
- Folder structure: `context/`, `projects/`, `decisions/`
- Claude finds files only by exact keyword match
- Relies on Claude Code's native **automemory** (auto-generates basic markdown notes in `.claude/memory/`)
- A lean `CLAUDE.md` acts as the "router" - tells Claude where information lives
- **Unlock:** Claude knows where to look; still can't connect dots

### Level 2 - Topic Aggregation: The LLM Wiki
- Claude reads raw source documents and autonomously writes, links, and maintains summarized wiki pages
- Uses index files to navigate thousands of documents without loading them all into context
- Architecture: **Andrej Karpathy's LLM Wiki** (3-layer structure, see below)
- **Obsidian** as the visual interface
- **Unlock:** a compounding, self-organizing knowledge base Claude writes itself

### Level 3 - Semantic Search: Vector RAG
- Upgrades from keyword matching to searching by meaning and intent
- If you search "feedback," it surfaces "live test results" and "evaluations" even if the exact word isn't used
- Tools: **Pinecone**, **Supabase** for vector databases
- **Unlock:** vast unstructured archives become searchable; good for policy PDFs, email history

### Level 4 - Knowledge Graphs & Relationship Chains
- Maps complex relationships: "Project A collaborates with Tool B, which was built by Person C"
- Lets you trace any concept back to its root cause
- Tools: **Graphify**, **LightRAG**, **Microsoft GraphRAG**
- The **"Grill Me"** skill (originally by Matt Pocock) extracts tacit knowledge from your own head to feed the graph
- **Unlock:** deep reasoning over relationships, not just retrieval

### Level 5 - The Autonomous Always-On Brain OS
- Runs 24/7: continuously syncs, refreshes memories, ingests new data (Slack threads, emails) while you sleep
- A "Top-of-Funnel" AI router decides whether a query needs a simple markdown lookup, a vector search, or a knowledge graph traversal
- Multimodal: parses meaning from video, tables, and images, not just text
- Tools: **GBrain** (Y Combinator CEO Gary Tan's concept), **Hermes** (always-on persistent agent), **Gemini embedding 2** for video/visual indexing
- **Unlock:** fully autonomous operating system; human on-the-loop, not in-the-loop

---

## The Core Architecture: Karpathy's LLM Wiki (3-Layer Structure)

Popularized by **Andrej Karpathy** (founding OpenAI, former Tesla AI Director). The analogy: Obsidian = the IDE, the LLM = the programmer, the wiki = the codebase.

**Why it beats traditional RAG:**
- Standard RAG: AI searches raw docs on every query, stitches an answer, forgets everything. Computationally expensive, struggles to connect dots.
- LLM Wiki: pre-computes knowledge. AI reads a new source once, updates 10-15 interconnected pages, logs what changed. Future queries hit the pre-built wiki, not raw data.

### The Three Layers

```
vault/
├── raw/          # Read-only intake folder. Drop PDFs, meeting transcripts, articles here.
│                 # AI reads but never modifies. Use Obsidian Web Clipper to save articles.
├── wiki/         # AI-written and maintained knowledge base. Interlinked markdown pages,
│                 # concept summaries, entity pages. Compounds in value over time.
│   ├── index.md  # Master catalog of all wiki pages; AI navigates via this
│   └── log.md    # Operation history: what the AI changed during each ingestion cycle
└── CLAUDE.md     # The rulebook/schema: who you are, how the wiki is structured,
                  # formatting rules, routing rules. Keep under 150-200 lines.
```

### Key operational commands
- **Ingest:** "I just added a new source to the raw folder. Please read it and update the wiki." Claude reads, extracts key concepts, creates/updates cross-referenced wiki pages.
- **Lint:** "Lint the wiki." Claude scans for orphaned pages, broken links, stale claims, missing data - same as a code linter.
- **Compact:** `/compact` when context approaches 60% of the window; Claude compresses conversation history into a summary block, preserving essential context.
- **Handoff:** `/handoff` to transfer session state to a clean new session; generates a markdown summary of current context.

---

## Key Tools Breakdown

### Obsidian (The Visual Layer / IDE)
- Free, local-first markdown app. Data = plain text `.md` files in a local "vault" folder. You own all data.
- **Graph view** maps how notes connect visually via internal links.
- In a second-brain setup: Claude Code runs in the terminal inside your Obsidian vault folder. Obsidian visualizes what Claude is building.

**Key integrations:**
- **Terminal Plugin** (community): open an integrated terminal inside Obsidian; run `claude` without leaving your notes
- **Obsidian Markdown Skill**: Claude Code skill that teaches the AI Obsidian-flavored markdown (wiki-links `[[note]]`, properties, tags, callouts)
- **Obsidian Web Clipper**: browser extension to save web articles directly into `/raw` as markdown
- **Graphify (`graphify . --obsidian`)**: auto-generates a graph + Obsidian-viewable map from any repository (PyPI package `graphifyy`)
- **Filesystem MCP**: for Cowork users (non-terminal), lets Claude Desktop read/write directly to your Obsidian folders

**What you can do with Claude + Obsidian:**
- Drop a 50-page PDF into `/raw`, ask Claude to ingest. Claude extracts key ideas, updates existing concept pages, creates new ones, links everything in the graph.
- Build a visual "command center" / AI OS with dashboards tracking daily tasks, token usage, and social media growth.
- Store client profiles, meeting transcripts, and business decisions - Claude acts as an executive assistant that knows exactly what happened last week.

### Graphify (The Knowledge Graph Builder)
- Open-source, ~60,000 GitHub stars. Turns any codebase, repository, or document collection into a **dynamic knowledge graph**.
- Solves Claude's two biggest limitations: context loss (amnesia) and token expenses.
- Without Graphify: Claude "greps" (scans) the entire codebase on every question - slow, expensive, misses connections.
- With Graphify: Claude queries a pre-built relationship map - reliably 40% fewer tokens (some users claim 70x).

**How Graphify works (3-pass system):**
1. **Code structure pass**: tree-sitter parses code deterministically (classes, functions, imports, call graphs) - no LLM, no API cost
2. **Multimedia pass**: Faster Whisper transcribes audio/video files and injects text into the graph
3. **Semantic analysis pass**: LLM extracts concepts from unstructured documents (PDFs, papers, images)

**Output structure:** nodes (concepts/files) + edges (how they relate) + communities (clusters) + "god nodes" (critical load-bearing files)

**Install + key commands** (verified 2026-06-20 via the repo, github.com/safishamsi/graphify):
- Install: `pip install graphifyy` (PyPI package is `graphifyy`, double-y; CLI command stays `graphify`). Alternatives: `uv tool install graphifyy`, `pipx install graphifyy`.
- `graphify hook install` - post-commit/post-checkout git hooks that auto-rebuild the graph on code-only changes at zero API cost (needs a git repo)
- `graphify . --obsidian` - builds the graph from a folder and produces `graph.html` (interactive map), `GRAPH_REPORT.md`, `graph.json`. Headless alt: `graphify extract ./src`.
- Inside a running `claude`/Cursor session, the slash form is `/graphify . --obsidian`. In a plain Windows terminal use `graphify .` (no leading slash - it's a path separator). NOTE: there is no separate `graphify-obsidian` command; it's the `--obsidian` flag.

**vs alternatives:**
- vs Traditional RAG: RAG uses vector embeddings good for policy PDFs, bad for code flow. Graphify does NOT use vector embeddings - optimized for architectural relationships.
- vs Obsidian alone: Obsidian requires manual linking. Graphify automates the entire mapping and can generate the vault for you.

### LLM Wiki / AI Wiki (Karpathy's Memory Architecture)
- See "Core Architecture" section above. Key distinction from regular knowledge bases: the AI writes and maintains the wiki, not the human.
- Uses markdown wiki-links (actual `[[page]]` links), not vector similarity search - traces deep relationships deterministically.
- 95% fewer tokens than re-reading raw transcripts per query.
- No vector databases required at this level.

### Claude Mem + Context Mode (Session Memory Plugins)
- **Claude Mem** (`claude-mem`, 35.9k+ stars): cross-session memory in a local SQLite vector database. Intercepts session lifecycle, captures every edited file and decision, compresses into semantic summaries.
- **Context Mode**: filters verbose shell output (npm logs etc.) from polluting the context window. Also enables SQLite session restore.
- Together: automatic capture-and-compress of everything Claude does across sessions.

### Vector RAG Layer (Level 3+)
- **Pinecone** or **Supabase**: chunk and embed unstructured archives for semantic search.
- Best for massive unstructured data (years of email, Slack history) - not for code relationships.
- **NotebookLM + NotebookLM CLI**: Google's notebook for massive archives - offloads analysis to Google's servers at near-zero token cost. Pair with a "Wrap-up" skill to save whole sessions into a "brain" notebook.

### AutoDream (Memory Consolidation - mid-2026 feature)
- Background sub-agent that runs between sessions. Automatically:
  - Prunes contradicted facts
  - Merges duplicate notes
  - Updates temporal references ("yesterday" -> specific date)
- Prevents the knowledge base from drifting on stale information.

---

## Step-by-Step Setup Guide

### Step 1: Install software
```powershell
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex   # Claude Code

# Download Obsidian from obsidian.md (free)
# Optional: install Graphify for large repos -> pip install graphifyy
```

### Step 2: Create vault + folder structure
1. Open Obsidian, create a new Vault (folder on your computer)
2. Open that folder in terminal, type `claude` to initialize Claude Code
3. Create the LLM Wiki folder structure:

```
your-vault/
├── raw/         # Drop source materials here
├── wiki/        # Claude builds knowledge base here
├── templates/   # Optional: manual note templates
└── CLAUDE.md    # The rulebook (create in Step 3)
```

### Step 3: Configure CLAUDE.md
Run `/init` to auto-generate a base file, then add:
- Define the architecture: where `raw/` and `wiki/` are
- Set the ingest workflow: when new source added, read, extract, create/update wiki pages, log changes
- Page formatting rules: every wiki page must have a summary, cite sources, link to related pages
- Routing rules (keep this file under 150-200 lines - every prompt reads it, bloating wastes tokens)

**Keep CLAUDE.md as a table of contents that points to specialized files, not a document containing everything.**

### Step 4: Feed the system
1. Drop files into `raw/` (PDFs, transcripts, articles via Web Clipper)
2. Prompt: "I just added a new source to the raw folder. Please read it and update the wiki."
3. Claude reads, extracts entities, updates cross-referenced pages, files into `wiki/`

### Step 5: Maintain memory health
- **`/compact`** when context hits ~60%: compresses conversation history, frees tokens
- **AutoDream** (if enabled): handles automatic pruning/merging between sessions
- **`/handoff`** when switching tasks: generates a session-state markdown for clean context transfer
- **Monitor context:** `/context` shows token usage %; once at ~20% of 1M window (200k tokens), `/clear` the session. Your knowledge is in the markdown files - Claude won't forget.

### Step 6: Pitfalls to avoid

| Pitfall | Fix |
|---------|-----|
| **Context rot / bloat** - keeping same session open forever | `/compact` at 60%, `/clear` at 200k tokens |
| **Overstuffed CLAUDE.md** - burns tokens on every prompt | Keep under 150-200 lines; use routing pointers, not full content |
| **Ingesting noisy data** - daily Slack threads, temp complaints | Only ingest evergreen data: goals, SOPs, long-term research |
| **Privacy risk** - sensitive client data or private keys | Use zero-data-retention Enterprise API tier, or keep sensitive data out entirely |

---

## Agency / Freelancer Setup

### Recommended folder structure (LLM Wiki + Four C's)

```
agency-brain/
├── CLAUDE.md              # The lean router/schema (under 200 lines)
├── context/               # Who & What (never changes much)
│   ├── brand_voice.md     # Sentence rhythm, vocabulary, banned words, approved phrasing
│   └── icp_and_offer.md   # Ideal client profile, service packages, value propositions
├── projects/              # Active Work (one subfolder per client)
│   └── [Client Name]/
│       ├── brief.md
│       ├── meeting-transcripts/
│       └── deliverables/
├── skills/                # Agency SOPs as markdown instruction files
│   ├── content_cascade.md
│   ├── proposal.md
│   └── onboarding.md
├── raw/                   # Staging area: call transcripts, PDF reports, brain dumps
├── wiki/                  # Claude's compiled knowledge base (auto-maintained)
└── decisions/             # Running log of strategy changes, milestones, decisions
```

### Example CLAUDE.md schema for an agency

```markdown
# Agency AI Operating System

## Role
You are the executive assistant and operational brain for [Agency Name].
Your goal is to automate client workflows, draft proposals, and manage content pipelines.

## Navigation & Routing Rules
- Brand Voice & Business Info: read files in /context
- SOPs: use instructions in /skills folder
- Client Data: /projects/[Client Name]
- Raw Data: new transcripts and notes in /raw

## Operating Principles
1. Think before executing: outline your plan before creating files
2. Maintain Voice: never write generic AI copy; strictly adhere to brand_voice.md
3. Surgical Changes: when editing client copy, only change what is requested
```

### Key agency use cases

**Client management & outreach**
- After a sales call: Claude scans the transcript, updates CRM fields (via HubSpot MCP connector), drafts a personalized follow-up email referencing specific pain points from the conversation.
- Tool: Claude Cowork + HubSpot MCP (part of "Claude for Small Business" package)

**Proposal generation**
- Drop: 200-page client RFP + past successful proposals + raw client brief into a folder
- Claude synthesizes, matches your pricing structures, generates a fully structured proposal draft
- 200K-1M token context window handles it; reduces drafting time ~40%

**Content creation: the Content Cascade**
- Feed one YouTube transcript or recorded meeting note into Claude
- A "Content Cascade" skill auto-converts it: blog post + LinkedIn carousel + Twitter thread, all in brand voice
- Claude's Canva integration can then autonomously generate on-brand graphics

**SOP execution (WAT Framework)**
- WAT: Workflows (plain-language SOPs) + Agent (Claude) + Tools (code exec, terminal)
- If you do a task 3+ times/week, write it as a Skill
- `/schedule` in Claude Cowork: runs the skill every Friday, pulls metrics, formats a PDF report, drops it in the client folder

**Advanced: NotebookLM for infinite memory**
- Store massive archives (every client email, past deliverable, all SOPs) in NotebookLM
- Connect via NotebookLM CLI as a skill/MCP
- Claude semantically searches the "long-term memory" database and retrieves only exact insights needed - prevents context window max-out

**Mobile dispatch**
- Dictate a client idea or meeting note into your phone
- Claude Dispatch sends it to your desktop; Claude Cowork formats it and has the draft ready when you arrive

---

## Integration Combos

| Combo | What it unlocks |
|-------|----------------|
| Claude Code + Obsidian | Visual second-brain; Claude builds the wiki, you navigate it |
| Graphify + Obsidian | Auto-generates a fully linked Obsidian vault from any codebase or doc repo |
| Claude Code + NotebookLM CLI | Infinite persistent memory at near-zero token cost; offloads analysis to Google |
| Claude Code + Firecrawl | Reliable scraping at scale: competitor pricing, lead-gen directories, market research |
| Claude Code + Playwright | End-to-end browser automation: QA, web task execution (more token-efficient than MCP) |
| Cowork + HubSpot MCP | Autonomous CRM management from call transcripts |
| Cowork + Canva MCP | Batch on-brand graphic generation from content calendar |

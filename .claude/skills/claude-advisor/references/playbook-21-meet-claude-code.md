# Advanced - Section 21: Meet Claude Code: AI That Builds

*The most powerful door, and why you don't need to be a coder to open it.*

**Bottom line:** Claude Code is Claude in a terminal or code editor, with the ability to read, write, and edit files across an entire project. It builds software, fixes bugs, designs systems, and runs automations across your full codebase. You do not need to be a programmer to start. But it rewards people who are willing to engage at a technical level.

---

## What Claude Code actually is

Claude Code is a command-line tool and IDE integration that gives Claude access to your file system, your terminal, and your codebase. Instead of responding in a chat window, it works inside your development environment: reading files, writing code, running commands, and iterating on the results.

The key difference from the chat interface: Claude Code can see and edit many files at once, run your code to test it, and make changes across an entire project, not just answer questions about it.

## You do not need to be a coder

That is not marketing language. Non-technical people use Claude Code to:

- Build working prototypes from a plain-English description
- Automate repetitive file operations and data processing
- Create scripts that run on a schedule without manual work
- Build internal tools (dashboards, reports, automators) without a development team

The pattern is: describe what you want in plain English, review what Claude builds, test it, iterate. You are the product manager; Claude is the developer.

## What it can do

- **Write code from scratch:** Give it a description, get working software.
- **Read and understand an existing project:** Point it at a codebase, ask it questions, ask it to add features.
- **Fix bugs:** Describe the problem or paste the error, and Claude diagnoses and patches it.
- **Refactor and clean up:** Improve existing code without changing what it does.
- **Write tests:** Generate automated tests for existing functionality.
- **Build automations:** Scripts, pipelines, and scheduled tasks that run without you.
- **Work across many files:** Unlike chat, it can hold an entire project in context and make changes consistently.

## Four-step setup

1. Install Node.js (free, at nodejs.org) if you do not have it. It is the runtime Claude Code needs.
2. Open a terminal (Mac: Terminal app, Windows: Command Prompt or PowerShell).
3. Run: `npm install -g @anthropic-ai/claude-code`
4. Navigate to a folder for your project and run: `claude`

That is it. Claude Code opens in the terminal, connected to your folder.

## Your first run

Once Claude Code is running:
- Tell it what you want to build: "Build me a script that reads all the CSV files in this folder, combines them, and outputs a summary spreadsheet."
- Watch what it does: it will read your folder, propose a plan, write the code, and run it.
- Review the output, test it, and iterate.

## Golden rules for non-coders using Claude Code

- **Work in a test folder first.** Do not point Claude Code at your main business files until you understand how it works.
- **Read what it proposes before saying yes.** The plan step is your quality gate.
- **Save working versions.** Use Git or simply copy a working version before asking for changes.
- **Ask Claude Code to explain what it did.** "Walk me through what that script does and why" is a legitimate instruction.

## Key takeaways

- Claude Code is Claude in a terminal or editor, working across your full project rather than in a chat window.
- Non-technical users build real tools with it. The pattern: describe in plain English, review the plan, test the output.
- Setup takes about 10 minutes (Node.js + npm install + claude command).
- Start in a test folder, read plans before approving, and use Git or manual copies to save working versions.

# Intermediate - Section 11: Meet Cowork: Your AI That Gets Things Done

*Claude stops answering and starts acting.*

**Bottom line:** Cowork is Claude running as an autonomous assistant on your actual desktop. You give it a goal in plain English, it does the work, and it asks permission at key moments. No coding required. This is the jump from "Claude helps me think" to "Claude does the work while I think about something else."

---

## What Cowork actually is

When you run Claude in a normal chat, you are in a back-and-forth conversation. You write, it replies, you write again. Cowork changes that dynamic. You give Claude a goal, point it at your computer (a folder, a file, an application), and it executes, step by step, using tools to open files, read content, write outputs, and organize results. You see what it is doing and approve or redirect the decisions that matter.

Think of it as hiring an extremely capable, extremely literal assistant. It does exactly what you say, asks when it is unsure, and shows its work.

## How the plan-to-action loop works

1. You give Cowork a goal: "Take all the feedback PDFs in this folder, extract the key themes from each, and build a summary spreadsheet with one row per document."
2. Cowork builds a plan and shows it to you before doing anything.
3. You confirm (or adjust) the plan.
4. It executes step by step, flagging any decisions that need your input.
5. You review the output at the end.

This loop matters because it keeps you in control without requiring you to do the work.

## The sandboxed VM

Cowork operates inside a sandboxed virtual machine, a contained computer environment. This means:
- What it does in the sandbox does not affect your real computer unless you explicitly move something out.
- If something goes wrong, nothing is permanently broken.
- You can reset the environment and start fresh.

## Ask Before Acting vs Act Without Asking

Two modes control how much Cowork interrupts you:

- **Ask Before Acting:** Cowork pauses before significant steps and waits for your approval. Best when you are learning Cowork, when the task is new, or when stakes are high.
- **Act Without Asking:** Cowork completes the full task and only surfaces something if it genuinely cannot proceed. Best for routine, well-understood tasks you have run before.

Start with Ask Before Acting until you trust how Cowork handles your type of task.

## Setting up Cowork (4 steps)

1. Open the Claude Desktop app.
2. Select Cowork from the mode options.
3. Point it at a folder you want to give it access to (or leave it at the default sandbox).
4. Describe your goal in plain English and confirm the plan.

## Good first task

"Take this folder of email threads, summarize the key decisions from each one, and put them in a table with columns for: thread subject, decision made, and next action."

Paste the folder path, run it in Ask Before Acting mode, and watch what it does. That 10-minute demo will teach you more about Cowork than reading about it.

## What Cowork is good at vs its limits

**Good at:**
- File organization and renaming
- Reading many documents and synthesizing them
- Building spreadsheets and reports from source material
- Batch operations on many files at once

**Limits:**
- It needs to access files through the paths you give it
- Complex multi-application workflows work best on the API (covered in Advanced)
- Anything requiring your real computer credentials or logged-in sessions needs care

> **Key mindset:** Cowork is not magic. It is a precise, literal assistant. The better your goal is defined, the better the output. If you would not know how to explain the task to a new hire in two paragraphs, break it down further before giving it to Cowork.

## Key takeaways

- Cowork runs Claude as an autonomous assistant on your desktop. You define the goal, it executes, you review.
- The plan-to-action loop (plan, confirm, execute, review) keeps you in control without doing the work.
- Start with Ask Before Acting mode. Switch to Act Without Asking once you trust the task.
- The sandboxed VM means nothing permanent happens to your machine without you moving something out.
- Best for file work, batch processing, document synthesis, and spreadsheet generation.

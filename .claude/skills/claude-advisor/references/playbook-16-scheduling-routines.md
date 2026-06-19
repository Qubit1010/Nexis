# Intermediate - Section 16: Scheduling and Routines: Claude on Autopilot

*Put the work that repeats on a schedule, so it just happens.*

**Bottom line:** The work that repeats every day or every week is a candidate for automation. Claude can run scheduled tasks, both locally on your computer and in the cloud. This section covers the two types, what to automate vs leave manual, and how to stay human-on-the-loop.

---

## Two types of scheduling

| Type | How it works | Best for |
|------|-------------|----------|
| Cowork local schedule | Claude Desktop runs the task on your computer at a set time, while your machine is on | Tasks that need local files, your apps, or your desktop state |
| Cloud Routines | Claude runs the task in the cloud on Anthropic's servers, on a schedule, without your computer being on | Tasks that are purely digital and do not need your local machine |

## Setting up a local schedule (Cowork)

Inside Claude Desktop and Cowork, you can set a task to run on a recurring schedule:

1. Build and test the task once manually. Confirm it produces the output you want.
2. Open the schedule settings and set the recurrence (daily at 8am, every Monday, the first of the month).
3. Set the output destination (a folder, a file, a location it can always write to).
4. Enable Ask Before Acting or Act Without Asking depending on how much you trust the routine.

This is best for: morning briefings from a local folder, weekly file processing, recurring reports from spreadsheets on your machine.

## Setting up a Cloud Routine

Cloud Routines let you define a scheduled task that runs on Anthropic's servers:

- Use the `/schedule` command in Claude Code or the Routines panel in Claude Desktop.
- Define what to do, when to run it, and where the output should go (a cloud folder, an email draft, a Notion page).
- It runs whether your computer is on or not.

This is best for: sending a weekly digest to your inbox, generating a Monday morning brief from web sources, any task that does not depend on your local files.

## What to automate vs leave manual

**Automate:**
- Recurring summaries and briefings (daily, weekly, monthly)
- Batch file processing on the same folder
- Regular reports from the same data source
- Reminders and check-ins that follow a fixed schedule

**Leave manual:**
- Tasks where the input changes unpredictably (you need to judge what to give it)
- Anything requiring real-time decisions you want to make yourself
- High-stakes outputs that go directly to clients without your review

## Running them well: stay human-on-the-loop

Scheduled tasks are not truly hands-off, they require oversight:

- **Review outputs regularly.** Run a new routine daily for the first two weeks and check every output. Catch drift early.
- **Set a quality gate.** For anything that goes to a client or gets sent externally, keep a manual review step before it leaves your control.
- **Log failures.** Configure the routine to notify you if it fails or produces no output. A silent failure is worse than an obvious one.
- **Update the routine when your process changes.** Stale routines produce stale outputs. Treat them like Skills: living documents.

> **The mindset:** Automation without oversight is just scheduled mistakes. Stay on the loop, not in it.

## Key takeaways

- Two scheduling types: local (Cowork, needs your machine) and cloud (Routines, runs on Anthropic's servers anytime).
- Automate what repeats and has a predictable input. Leave manual what requires your judgment each time.
- Review automated outputs for the first two weeks of any new routine. Catch problems before they become habits.
- Human-on-the-loop means you review and approve, not that you do the work. That is the right level of automation for most people.

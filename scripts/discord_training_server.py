"""Build out the NexusPoint Claude Code Training Discord server.

Creates roles, categories, channels and read-only permissions, then posts the
rules, the resources seed and Task 01. Idempotent: re-running skips anything
that already exists and never double-posts.

Setup (one time):
  1. https://discord.com/developers/applications -> New Application
  2. Bot tab -> Reset Token -> copy it -> put DISCORD_BOT_TOKEN=<token> in .env
  3. Bot tab -> enable "Message Content Intent" (not strictly needed, but avoids surprises later)
  4. OAuth2 -> URL Generator -> scopes: bot -> permissions: Administrator
     -> open the generated URL, add the bot to the training server
  5. python scripts/discord_training_server.py

  ponytail: raw REST over discord.py. This is a one-shot admin job, no gateway
  connection needed. Swap to discord.py only if this grows into a live bot.
"""

import os
import sys
import time

import requests

API = "https://discord.com/api/v10"
GUILD_NAME = "NexusPoint Claude Code Training"

# Permission bits (https://discord.com/developers/docs/topics/permissions)
VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
ADD_REACTIONS = 1 << 6
SEND_MESSAGES_IN_THREADS = 1 << 38
CREATE_PUBLIC_THREADS = 1 << 35
ATTACH_FILES = 1 << 15
EMBED_LINKS = 1 << 14

TEXT, VOICE, CATEGORY = 0, 2, 4


def load_token():
    """Read DISCORD_BOT_TOKEN from the environment or the repo .env."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        return token.strip()
    env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env):
        with open(env, encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("DISCORD_BOT_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("DISCORD_BOT_TOKEN not found. Add it to .env (see the setup steps at the top of this file).")


SESSION = requests.Session()


def api(method, path, **kwargs):
    """Call the Discord API, retrying once per 429 until it clears."""
    while True:
        r = SESSION.request(method, API + path, timeout=30, **kwargs)
        if r.status_code == 429:
            wait = r.json().get("retry_after", 1)
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait + 0.5)
            continue
        if r.status_code >= 400:
            sys.exit(f"{method} {path} failed [{r.status_code}]: {r.text}")
        return r.json() if r.text else {}


def find_guild():
    guilds = api("GET", "/users/@me/guilds")
    for g in guilds:
        if g["name"] == GUILD_NAME:
            return g["id"]
    if len(guilds) == 1:
        print(f"Guild '{GUILD_NAME}' not found by name, using the only guild: {guilds[0]['name']}")
        return guilds[0]["id"]
    sys.exit(f"Could not find guild '{GUILD_NAME}'. Bot is in: {[g['name'] for g in guilds]}")


# --- Server definition -------------------------------------------------------

ROLES = [
    # (name, colour, hoisted)
    ("Instructor", 0xF1C40F, True),
    ("Level 3 - Operator", 0x9B59B6, True),
    ("Level 2 - Builder", 0x3498DB, True),
    ("Level 1 - Learner", 0x95A5A6, True),
]

# (category, [(channel, type, read_only, topic)])
STRUCTURE = [
    ("START HERE", [
        ("announcements", TEXT, True, "Anything you must not miss. Read-only."),
        ("rules", TEXT, True, "How this server works and what is expected of you. Read-only."),
    ]),
    ("LEARN", [
        ("lessons", TEXT, True, "Claude Code advice, patterns and walkthroughs. Reply in threads."),
        ("resources", TEXT, True, "Docs, cheatsheets and links worth keeping. Read-only."),
        ("questions", TEXT, False, "Stuck? Ask here, not in DMs. Show your prompt and the output."),
    ]),
    ("PRACTICE", [
        ("task-board", TEXT, True, "Assigned tasks. One thread per task, discuss inside the thread."),
        ("submissions", TEXT, False, "Post finished tasks here: what you built, your prompts, what you would change."),
        ("wins", TEXT, False, "Something Claude Code did for you that would have taken hours. Share it."),
    ]),
    ("GENERAL", [
        ("general", TEXT, False, "Anything that does not belong in another channel."),
        ("General", VOICE, False, None),
        ("Pair Session", VOICE, False, None),
    ]),
]

RULES_MESSAGE = """**How this server works**

This server exists for one reason: to get you good enough at Claude Code to use it on real client work. Not demos. Real work.

**The rules**

**1. Ask in #questions, not in my DMs.**
If you have the question, someone else has it too. The answer is worth more in public.

**2. Show your prompt.**
"It didn't work" is not a question. Post what you typed, what came back, and what you expected instead. Ninety percent of the time you will spot the problem while writing it out.

**3. Thirty minutes, then ask.**
Stuck longer than that and you are not learning, you are just stuck. There is no prize for suffering quietly.

**4. Tasks live in #task-board.**
Each task gets its own thread. Discuss it there. Post the finished thing in #submissions.

**5. Every submission includes three things.**
What you built. The prompts that got you there. What you would do differently next time. The third one is the one that actually teaches you something.

**6. Never paste credentials.**
No API keys, no client data, no passwords. Not in prompts, not in screenshots, not "just for testing".

**7. Read the output before you ship it.**
Claude is confident when it is wrong. You are responsible for what you deliver, not the model.

**Levels**

`Level 1 - Learner` you are here
`Level 2 - Builder` first task accepted
`Level 3 - Operator` shipped something that gets used on real work

You move up by doing the tasks. That is the only way."""

RESOURCES_MESSAGE = """**Start with these**

Claude Code docs
https://docs.claude.com/en/docs/claude-code/overview

Best practices for agentic coding
https://www.anthropic.com/engineering/claude-code-best-practices

Common workflows
https://docs.claude.com/en/docs/claude-code/common-workflows

CLAUDE.md and memory
https://docs.claude.com/en/docs/claude-code/memory

Skills
https://docs.claude.com/en/docs/claude-code/skills

MCP
https://docs.claude.com/en/docs/claude-code/mcp

Read the first two properly before you ask anything in #questions. Most beginner problems are answered in those."""

# Discord caps a message at 2000 chars, so this posts as two.
TASK_01_MESSAGE = ["""**TASK 01 - Strategic Foundation Engine**

**Assigned to:** Areeba
**Timebox:** 2 days
**Type:** Capability test, not client work

**The goal**
Build a Claude skill called Strategic Foundation Engine. Someone hands it a business, either an idea or a company that already exists, and the skill produces that business's strategic foundation.

**What the skill has to produce**
These five are the scope. The list is fixed, everything else is your call.

1. Mission, vision and values
2. Market research and a defined target customer
3. Competition and industry trend analysis
4. A unique value proposition
5. A business plan and financial forecast covering revenue model, cost structure and funding needs

**Deliverable**
A folder named `strategic-foundation-engine/` containing at minimum a `SKILL.md`. Whatever else goes inside it, references, scripts, templates, is your decision and is part of what I am assessing.

Send three things:
- The folder
- A short note, half a page maximum: how you decided what goes in SKILL.md versus a separate file, what you deliberately left out and why, and anything you were unsure about
- One worked example. Run your finished skill on a real business and attach the output. Use NexusPoint or any company you know well enough to catch it being wrong.""",
"""**Rules for this task**
- Read `.claude/rules/` before you start and apply what is relevant. Some of it applies directly to a skill like this one.
- Look at two or three existing skills in `.claude/skills/` first. Match the house pattern.
- There is a `skill-creator` skill in the repo. Using it is your choice. If you skip it, say why in your note.
- Do not install this into Nexis. Build it standalone and send the folder. It gets reviewed first.

**Done means**
A fresh Claude session can load your SKILL.md and do the job without you sitting there explaining it. All five pieces get produced, not just described. The worked example is attached and is actually usable.

**One warning**
The financial forecast is the easiest place in this task to produce confident nonsense. Decide how your skill handles numbers it cannot know, and make that decision visible inside the skill itself.

Two days. If you hit day two and it is not done, send what you have plus what is left. Stopping on time counts.

Questions in the thread below."""]


# --- Builders ----------------------------------------------------------------

def ensure_roles(guild):
    existing = {r["name"]: r for r in api("GET", f"/guilds/{guild}/roles")}
    ids = {}
    for name, colour, hoist in ROLES:
        if name in existing:
            print(f"  role exists: {name}")
            ids[name] = existing[name]["id"]
            continue
        role = api("POST", f"/guilds/{guild}/roles", json={
            "name": name, "color": colour, "hoist": hoist, "mentionable": True, "permissions": "0",
        })
        print(f"  role created: {name}")
        ids[name] = role["id"]
        time.sleep(0.5)
    return ids


def order_roles(guild, ids):
    """Rank the roles so the level ladder reads top-down in the member list.

    Roles created via the API all land at position 1, which leaves Discord to
    order them arbitrarily. The bot sits above them all so it can still manage
    them; it is unhoisted, so it shows no sidebar group of its own.
    """
    me = api("GET", "/users/@me")["id"]
    bot_role = next((r["id"] for r in api("GET", f"/guilds/{guild}/roles")
                     if r.get("tags", {}).get("bot_id") == me), None)
    ladder = [ids[name] for name, _, _ in ROLES]  # already ordered high to low
    if bot_role:
        ladder.insert(0, bot_role)
    payload = [{"id": rid, "position": len(ladder) - i} for i, rid in enumerate(ladder)]
    api("PATCH", f"/guilds/{guild}/roles", json=payload)
    print("  ranked: " + " > ".join(name for name, _, _ in ROLES))


def overwrites(guild, instructor_id, read_only):
    if not read_only:
        return []
    return [
        {
            "id": guild,  # @everyone role id == guild id
            "type": 0,
            "allow": str(VIEW_CHANNEL | ADD_REACTIONS | SEND_MESSAGES_IN_THREADS),
            "deny": str(SEND_MESSAGES | CREATE_PUBLIC_THREADS),
        },
        {
            "id": instructor_id,
            "type": 0,
            "allow": str(SEND_MESSAGES | CREATE_PUBLIC_THREADS | ATTACH_FILES | EMBED_LINKS),
            "deny": "0",
        },
    ]


def build_channels(guild, instructor_id):
    existing = api("GET", f"/guilds/{guild}/channels")
    # Key on name AND type: a server can hold a category, a text channel and a
    # voice channel all called "general", and keying on name alone collapses them.
    by_name = {(c["name"].lower(), c["type"]): c for c in existing}
    created = {}

    for cat_name, channels in STRUCTURE:
        cat = by_name.get((cat_name.lower(), CATEGORY))
        if cat:
            cat_id = cat["id"]
            print(f"category exists: {cat_name}")
        else:
            cat_id = api("POST", f"/guilds/{guild}/channels",
                         json={"name": cat_name, "type": CATEGORY})["id"]
            print(f"category created: {cat_name}")
            time.sleep(0.5)

        for ch_name, ch_type, read_only, topic in channels:
            found = by_name.get((ch_name.lower(), ch_type))
            if found:
                # Channel already exists (e.g. the default #general). File it and fix perms.
                patch = {"parent_id": cat_id}
                if topic and ch_type == TEXT:
                    patch["topic"] = topic
                if read_only:
                    patch["permission_overwrites"] = overwrites(guild, instructor_id, True)
                api("PATCH", f"/channels/{found['id']}", json=patch)
                print(f"  channel updated: {ch_name}")
                created[ch_name] = found["id"]
            else:
                body = {"name": ch_name, "type": ch_type, "parent_id": cat_id,
                        "permission_overwrites": overwrites(guild, instructor_id, read_only)}
                if topic and ch_type == TEXT:
                    body["topic"] = topic
                ch = api("POST", f"/guilds/{guild}/channels", json=body)
                print(f"  channel created: {ch_name}")
                created[ch_name] = ch["id"]
            time.sleep(0.5)
    return created


def drop_empty_categories(guild):
    """Remove leftover default categories, but only once nothing lives in them."""
    channels = api("GET", f"/guilds/{guild}/channels")
    ours = {name.lower() for name, _ in STRUCTURE}
    parents = {c.get("parent_id") for c in channels}
    for c in channels:
        if c["type"] == CATEGORY and c["name"].lower() not in ours and c["id"] not in parents:
            api("DELETE", f"/channels/{c['id']}")
            print(f"  removed empty category: {c['name']}")
            time.sleep(0.5)


def post_once(channel_id, content, pin=False):
    """Post only if this channel has no bot messages yet, so re-runs are safe.

    `content` is one message or a list of messages posted in order; only the
    first is pinned.
    """
    me = api("GET", "/users/@me")["id"]
    history = api("GET", f"/channels/{channel_id}/messages", params={"limit": 50})
    if any(m["author"]["id"] == me for m in history):
        print("  already posted, skipping")
        return None
    first = None
    for part in [content] if isinstance(content, str) else content:
        msg = api("POST", f"/channels/{channel_id}/messages", json={"content": part})
        first = first or msg["id"]
        time.sleep(0.5)
    if pin:
        api("PUT", f"/channels/{channel_id}/pins/{first}")
    print("  posted")
    return first


def main():
    SESSION.headers.update({
        "Authorization": f"Bot {load_token()}",
        "Content-Type": "application/json",
        "User-Agent": "NexisTrainingSetup (https://nexus-point.co, 1.0)",
    })

    guild = find_guild()
    print(f"Guild: {guild}\n")

    print("Roles:")
    roles = ensure_roles(guild)
    order_roles(guild, roles)
    print()

    channels = build_channels(guild, roles["Instructor"])
    print("\nCleanup:")
    drop_empty_categories(guild)
    print()

    print("Posting rules:")
    post_once(channels["rules"], RULES_MESSAGE, pin=True)
    print("Posting resources:")
    post_once(channels["resources"], RESOURCES_MESSAGE, pin=True)
    print("Posting Task 01:")
    post_once(channels["task-board"], TASK_01_MESSAGE, pin=True)

    print("\nDone. Remaining manual steps:")
    print("  - Give yourself the Instructor role (Server Settings > Members)")
    print("  - Invite the team, assign Level 1 - Learner on join")


if __name__ == "__main__":
    main()

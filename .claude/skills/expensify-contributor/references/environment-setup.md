# One-time setup

Split into what you need to win a proposal, and what you only need once you have won one. The
second half is more expensive, and deferring it is deliberate: there is no reason to buy Mac time
before anything has been accepted.

## Needed to compete for proposals

### The GitHub CLI

Every script here reads GitHub through `gh`, so it inherits your existing login rather than managing
a token. Check with `gh auth status`. If it is not installed, get it from https://cli.github.com and
run `gh auth login`.

### A local clone, outside OneDrive

```bash
python scripts/repo.py --ensure
```

Clones to `C:\dev\expensify-app` by default; override with `EXPENSIFY_REPO_PATH`. The script refuses
a OneDrive path, because a React Native checkout plus `node_modules` under a syncing folder produces
constant upload churn and occasional file locks during builds.

It uses `--filter=blob:none`, which brings the full commit history without downloading every
historical blob. Measured result: **782MB instead of 2.8GB**, with all files present at HEAD.

Two things to expect. The first `git` command after cloning triggers an automatic repack that
expands about 308,000 commits into the commit graph and takes several minutes. It looks like a hang
and is not; let it finish once. And `git blame` is pathologically slow on this kind of clone, since
it lazily fetches a historical blob per candidate commit over the network. That is why
`repo.py --blame` uses GitHub's GraphQL blame API instead, which also returns the associated pull
request, something local blame cannot do on squashed history.

### A test account

Create accounts directly in the app with a `+` suffix, for example `you+exp1@gmail.com`. The suffix
marks them as test accounts so Expensify's onboarding team is not assigned to help you.

Do not test against Concierge, and do not post in Expensify-owned public rooms. Both are covered in
`what-not-to-do.md` and both reach real people.

### Your Upwork profile link in your GitHub bio

`CONTRIBUTING.md` asks for this and ties it to prompt payment. Your profile must be fully verified
before applying to a job, or you risk not being paid.

## Needed only after a proposal is accepted

### Node 26.5.0

Pinned in `.nvmrc`, with `bun 1.3.14` and `npm 11.17.0` in `package.json` engines. Use nvm-windows:

```bash
nvm install 26.5.0
nvm use 26.5.0
```

Many of the repo's npm scripts are `.sh` files, so run them from Git Bash rather than PowerShell.

Check the current pins before installing rather than trusting these numbers, since they move:

```bash
cat /c/dev/expensify-app/.nvmrc
node -p "JSON.stringify(require('/c/dev/expensify-app/package.json').engines)"
```

### Signed commits

Every commit must be GPG-signed. Generate a key, add it to your GitHub account, then:

```
[commit]
    gpgsign = true
[user]
    email = <your GitHub account email>
    name = <your name>
    signingkey = <your signing key>
[gpg]
    program = gpg
```

### A Mac, for iOS and macOS testing

This is the real constraint. Expensify requires testing on iOS, macOS, Android, Web and mWeb, with
screenshots or video per platform in the pull request.

`contributingGuides/TESTING_MACOS_AND_IOS.md` documents the workaround and compares the options.
Scaleway M1 Mac minis at **$2.7 per day** are by far the cheapest; MacInCloud is $35 per month,
MacStadium $132 per month, AWS $26 per day. Access over VNC first, then set up Chrome Remote Desktop
because VNC is too slow to work in.

Against a $250 bounty, a few days of Scaleway is a rounding error. Against zero accepted proposals
it is pure cost, which is why it belongs here rather than in the first half. Until it is arranged,
`triage.py` scores iOS and macOS-only issues as unreachable, which is a genuine narrowing of an
already small funnel.

## Verifying the setup

```bash
python scripts/watch.py --selftest      # GitHub access and window classification
python scripts/triage.py --selftest     # the scoring rubric
python scripts/proposals.py --selftest  # proposal parsing and duplicate screening
python scripts/repo.py --selftest       # permalink generation and its guard rails
python scripts/post.py --selftest       # the posting guards
```

Each checks itself against issues whose outcomes are already settled, so a failure means something
really has changed rather than that a test is stale. `repo.py` reports SKIPPED rather than passing
when no clone exists, because a check that silently passes without running teaches you to trust
something that is not happening.

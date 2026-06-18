"""One-off runner: push new Instagram leads to CRM with BLANK Touch 1 DMs.

Reuses all of instagram_push.main()'s filtering / dedup / append / writeback,
but neutralizes Touch 1 generation (OpenAI quota is exhausted). DMs are filled
later via:  python instagram_push.py --refresh-touch1
"""
import sys
import instagram_push

# Neutralize DM generation -> empty Touch 1 (no OpenAI calls)
instagram_push.generate_touch1_dm = lambda lead: ""

# Run live (no --dry-run)
sys.argv = ["instagram_push.py"]
instagram_push.main()

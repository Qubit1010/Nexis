import json, sys
with open(r"c:\Users\qubit\OneDrive\Documents\Automations\Nexis\.claude\skills\client-onboarding-workflow-workspace\iteration-1\eval-1-doc-driven\without_skill\outputs\onboarding_spec.json", encoding="utf-8-sig") as f:
    data = json.load(f)
sys.stdout.write(json.dumps(data))
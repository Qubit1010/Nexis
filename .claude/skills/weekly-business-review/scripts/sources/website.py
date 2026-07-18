"""Website + lead-magnet analytics -- phase 2 placeholder.

nexus-point.co has GA4 + Search Console + a MailerLite lead-magnet form, but no API
access is wired yet (GA4/Search Console need OAuth or a service account; MailerLite
needs an API key). This section renders a 'coming in phase 2' state until that auth
is set up. The personal site is not yet instrumented.
"""


def collect(monday, sunday):
    return {
        "available": False,
        "phase": 2,
        "reason": "GA4 / Search Console / MailerLite API access not wired yet",
        "planned": [
            "GA4: sessions, users, top pages, top locations",
            "Search Console: clicks, impressions, top queries",
            "MailerLite: lead-magnet form signups",
        ],
        "sites": {"agency": "nexus-point.co (instrumented, not yet API-connected)",
                  "personal": "not yet instrumented"},
    }

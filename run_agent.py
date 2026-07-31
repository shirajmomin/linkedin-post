"""Generate one daily LinkedIn post draft (FHIR / CMS interoperability / health tech).

Usage:
  python run_agent.py
  python run_agent.py --no-ai
  python run_agent.py --no-email
  python run_agent.py --topic "CMS-0057-F PAS"
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai import call_llm
from common import cleanup_runtime_files, env, load_profile, load_prompt
from linkedin_image import create_post_image
from send_email import send_text


TOPIC_BANK = [
    "HL7 FHIR R4 resource modeling — why clean profiles beat one-off extensions",
    "CMS Patient Access API — what payers still get wrong about member experience",
    "Provider Directory API — data quality as the real interoperability bottleneck",
    "CMS-0057-F Prior Authorization — CRD: when coverage requirements should surface",
    "CMS-0057-F — DTR and the documentation burden on clinicians and payers",
    "CMS-0057-F — PAS: designing a reliable prior-auth submission path",
    "FHIR Bulk Data / $export — practical patterns for analytics pipelines",
    "Azure API Management for FHIR APIs — auth, throttling, and observability",
    "SMART on FHIR and app launch — security tradeoffs architects must own",
    "Medicare vs commercial payer interop — same standards, different constraints",
    "Technical leadership on interoperability programs — sequencing delivery risk",
    "How AI assistants change FHIR implementation work — and what still needs humans",
    "USCDI and FHIR US Core — mapping clinical data without breaking consumers",
    "Interoperability testing strategy — synthetic data, negative tests, and contracts",
    "From EDI 837/834 roots to FHIR APIs — what to keep and what to leave behind",
]

_FALLBACK_BODIES: dict[str, tuple[str, str]] = {
    TOPIC_BANK[0]: (
        "Clean FHIR profiles beat one-off extensions.",
        """A FHIR R4 model that "works in the demo" often collapses in production when every team invents its own extension.

I keep coming back to the same rule: constrain first with profiles and terminology bindings, then extend only when the use case is truly net-new. One-off extensions feel fast. They become the debt that breaks Patient Access consumers, Provider Directory clients, and Prior Auth (CRD/DTR/PAS) workflows later.

If you are designing a payer or platform FHIR layer this quarter, ask: would a third-party app interpret this resource the same way your internal team does?

Clean contracts scale. Clever extensions rarely do.

#FHIR #HL7FHIR #HealthIT #Interoperability #HealthcareArchitecture #CMSInteroperability""",
    ),
    TOPIC_BANK[1]: (
        "Patient Access API gaps show up as member friction.",
        """CMS Patient Access API compliance is not the same as a usable member experience.

I see payers ship FHIR endpoints that pass a checklist, then members still hit incomplete claims history, thin ExplanationOfBenefit payloads, or auth flows that apps cannot complete. The standard opened the door. Data readiness and API product thinking decide whether anyone walks through it.

Architecture question worth asking weekly: if a third-party app called your Patient Access endpoints today, what would disappoint a real member first?

#PatientAccessAPI #FHIR #CMSInteroperability #HealthIT #Payer #HealthcareTechnology""",
    ),
    TOPIC_BANK[2]: (
        "Provider Directory quality is the silent interop failure.",
        """Provider Directory APIs fail quietly. The FHIR looks fine. The phone numbers, specialties, and network status do not.

For CMS interoperability, directory quality is not a data-entry problem alone. It is an ownership problem across credentialing, network management, and the API platform. Stale NPI attributes and mismatched locations break member find-care journeys and downstream Prior Auth context.

If your directory FHIR resources are live, what is your freshness SLA — and who gets paged when it slips?

#ProviderDirectory #FHIR #CMSInteroperability #HealthIT #HealthcareData #Payer""",
    ),
    TOPIC_BANK[3]: (
        "CRD should surface coverage requirements early.",
        """CMS-0057-F CRD is powerful when coverage requirements show up in the clinical workflow — not after the claim is denied.

The architectural win is timing: CDS Hooks + FHIR context at the decision point, so clinicians see what documentation and auth rules apply before ordering. The failure mode is treating CRD as a bolted-on check that fires too late or with incomplete patient/encounter context.

If you are implementing CRD now, where does the hook land in your EHR workflow — and is the response actionable in under a few seconds?

#CMS0057F #CRD #PriorAuthorization #FHIR #HealthIT #Interoperability""",
    ),
    TOPIC_BANK[4]: (
        "DTR only helps if documentation asks are precise.",
        """DTR under CMS-0057-F can reduce Prior Auth friction — or multiply form fatigue.

The difference is questionnaire design and mapping to real clinical data. Vague documentation templates create click-burden. Tight questionnaires, pre-population from FHIR resources, and clear "why we need this" language create adoption.

When teams struggle with DTR, I usually look at the questionnaire library before the FHIR transport.

What is harder in your program: building the Questionnaire, or wiring it to source systems?

#DTR #CMS0057F #PriorAuthorization #FHIR #HealthIT #ClinicalWorkflow""",
    ),
    TOPIC_BANK[5]: (
        "PAS succeeds when submission paths are boringly reliable.",
        """PAS is the CMS-0057-F piece that turns Prior Auth from phone/fax theater into an API contract.

Reliability matters more than cleverness: idempotent submissions, clear ClaimResponse handling, status polling or subscriptions, and operational runbooks when a payer endpoint is slow. Interoperability programs stall when PAS is demoed once and never load-tested against real denial and pended scenarios.

If you run PAS today, can you replay a failed submission without creating duplicate auth requests?

#PAS #CMS0057F #PriorAuthorization #FHIR #HealthIT #APIManagement""",
    ),
    TOPIC_BANK[6]: (
        "Bulk Data fails when ops is an afterthought.",
        """FHIR Bulk Data / $export looks simple in a lab: kick off a job, poll, download NDJSON.

In production, the hard parts are tenancy isolation, partial failure, re-export windows, and how analytics teams actually consume the files without turning your FHIR server into a batch warehouse. I have seen clean CapabilityStatements paired with overnight jobs that stall because nobody owned storage lifecycle or access auditing.

If you are standing up $export, design the operational contract first — retention, retry, alerting — then celebrate the happy-path demo.

#BulkData #FHIR #HealthIT #Interoperability #HealthcareAnalytics #CMSInteroperability""",
    ),
    TOPIC_BANK[7]: (
        "APIM is where FHIR security becomes real.",
        """Azure API Management will not fix a weak FHIR design — but it will expose one.

AuthZ boundaries, client credentials vs SMART scopes, throttling for noisy consumers, and tracing across Patient Access / Directory / Prior Auth routes are product decisions, not just platform toggles. Treat APIM policies as part of your interop architecture review, not a last-mile checkbox.

What is one APIM policy you refuse to ship without on a healthcare API?

#Azure #APIManagement #FHIR #HealthIT #HealthcareArchitecture #CMSInteroperability""",
    ),
    TOPIC_BANK[8]: (
        "SMART launch security is an architecture choice.",
        """SMART on FHIR app launch is where security theater meets clinical workflow.

Token lifetimes, launch context integrity, EHR vs standalone flows, and what you put in the ID token vs access token all become production incidents when treated as "library defaults." Architects own the threat model — especially when third-party apps sit in front of member or clinician data.

If you reviewed your SMART launch path tomorrow, what would you test first: redirect hygiene, scope creep, or context spoofing?

#SMARTonFHIR #FHIR #HealthIT #HealthcareSecurity #Interoperability #APIManagement""",
    ),
    TOPIC_BANK[9]: (
        "Same FHIR standards. Different payer constraints.",
        """Medicare Advantage and commercial lines can share the same FHIR profiles and still need different operating models.

Coverage rules, network constructs, and member identity resolution diverge even when US Core looks familiar. Programs stall when teams assume "one Patient Access stack" without mapping those constraints into data contracts and SLAs.

Where do you feel the gap more today: clinical data completeness, or claims/coverage semantics?

#Medicare #Payer #FHIR #CMSInteroperability #HealthIT #HealthcareTechnology""",
    ),
    TOPIC_BANK[10]: (
        "Interop programs fail on sequencing, not standards.",
        """Technical leadership on interoperability is mostly sequencing risk.

Ship Directory quality before you market find-care experiences. Stabilize identity and consent before you open Patient Access floodgates. Prove CRD context before you scale DTR questionnaires. FHIR is the contract language — delivery order decides whether clinicians and members feel progress or churn.

What risk are you deliberately sequencing first this quarter?

#TechnicalLeadership #FHIR #CMSInteroperability #HealthIT #PriorAuthorization #HealthcareArchitecture""",
    ),
    TOPIC_BANK[11]: (
        "AI helps FHIR work. Humans still own the contract.",
        """AI assistants can draft CapabilityStatements, map extensions, and summarize IG text faster than any of us did five years ago.

They still cannot own semantic decisions: when an extension is justified, how a Questionnaire should behave in clinic, or whether a Prior Auth response is operationally safe. Use AI to accelerate drafting. Keep humans on profile governance and production sign-off.

Where are you letting AI help today — and where do you still require a human architect gate?

#AI #FHIR #HealthIT #HealthcareArchitecture #Interoperability #CMSInteroperability""",
    ),
    TOPIC_BANK[12]: (
        "US Core mapping is consumer protection.",
        """USCDI and FHIR US Core are not paperwork. They are how you stop every partner from inventing a private dialect.

The pain shows up in Must Support choices, terminology bindings, and what you do when source systems cannot populate a required element cleanly. Map for the consumer app, not for your internal warehouse comfort.

If a third-party app only trusted US Core, what would break first in your current feed?

#USCDI #USCore #FHIR #HealthIT #Interoperability #HealthcareData""",
    ),
    TOPIC_BANK[13]: (
        "Interop testing needs negative paths.",
        """Happy-path FHIR demos hide the bugs that matter.

Synthetic patients, expired tokens, empty Bundles, conflicting Identifier systems, and pended Prior Auth responses are where Patient Access and CMS-0057-F stacks actually fail. Build a contract test suite that prefers negative cases — then wire it into CI before the next partner onboarding.

What negative test do you wish you had run before your last go-live?

#InteropTesting #FHIR #HealthIT #CMSInteroperability #APIManagement #HealthcareTechnology""",
    ),
    TOPIC_BANK[14]: (
        "Keep EDI wisdom. Leave EDI coupling behind.",
        """Moving from 837/834 roots to FHIR APIs is not a lift-and-shift of X12 into JSON.

Keep the operational wisdom: reconciliation, acknowledgment semantics, partner onboarding discipline. Leave behind the assumption that every clinical or member journey must wait on a batch file window. FHIR consumers expect interactive contracts; your claims heritage still informs identity and coverage truth.

What is one EDI-era practice you are deliberately keeping in your FHIR program?

#EDI #FHIR #HealthIT #Payer #Interoperability #HealthcareArchitecture""",
    ),
}


def pick_topic(override: str | None = None) -> str:
    if override:
        return override.strip()
    # No history file — pick a random topic each run
    import random

    return random.choice(TOPIC_BANK)


def _profile_url() -> str:
    return load_profile().get("linkedin_url") or "https://www.linkedin.com/in/shiraj-momin-25610232/"


def _fallback_visual(topic: str, hook: str) -> dict[str, Any]:
    """HUD-style visual briefs matching premium HealthTech LinkedIn posts."""
    t = topic.lower()
    short = hook if len(hook) <= 56 else " ".join(hook.split()[:8])

    if "pas" in t or "0057" in t or "prior auth" in t or "prior-auth" in t or "crd" in t or "dtr" in t:
        return {
            "image_layout": "hud_alert",
            "alert_label": "DON'T DELAY",
            "image_title": "CMS-0057-F Deadline",
            "highlight": "January 1, 2027",
            "intro": "Electronic prior authorization is no longer optional for impacted payers.",
            "image_subtitle": "January 1, 2027",
            "bullets": [
                "Prior Authorization APIs must be live and production-ready",
                "CRD, DTR, and PAS require real end-to-end testing — not demos",
                "Provider Directory + clinical context must connect cleanly",
                "Late testing is the #1 reason programs miss go-live",
            ],
            "rail_labels": ["Patient Overview", "Interoperability", "Document Exchange"],
            "cta": "The deadline is closer than it looks. Start now.",
            "footer_note": "Build · Test · Validate FHIR prior-auth workflows before the deadline.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "steps": [],
            "badge_labels": ["CMS-0057-F", "PAS", "CRD", "DTR"],
            "accent_theme": "dark_green",
        }
    if "edi" in t or "837" in t or "834" in t:
        return {
            "image_layout": "hud_split",
            "alert_label": "ARCHITECTURE CHOICE",
            "image_title": "Stop grouping HL7 and FHIR as one bucket",
            "highlight": "Two standards. Two business realities.",
            "left_label": "HL7 v2: Operational Tax",
            "left_points": ["Point-to-point fragility", "High maintenance cost", "Hard to productize"],
            "right_label": "FHIR: Growth Engine",
            "right_points": ["Reusable APIs", "Faster onboarding", "Member-ready access"],
            "bullets": [],
            "rail_labels": [],
            "cta": "Architect for the model you want to operate.",
            "footer_note": "FHIR · HL7 · Interoperability",
            "steps": [],
            "badge_labels": ["HL7 v2", "FHIR", "API", "Scale"],
            "accent_theme": "dark_green",
        }
    if "patient access" in t:
        return {
            "image_layout": "hud_alert",
            "alert_label": "MEMBER EXPERIENCE",
            "image_title": "Patient Access API gaps show up as friction",
            "highlight": "Compliance ≠ experience",
            "intro": "A checklist pass is not the same as a usable member app journey.",
            "bullets": [
                "Incomplete claims / EOB payloads break trust fast",
                "Auth flows must complete for real third-party apps",
                "Data readiness decides whether anyone uses the API",
                "Test with a consumer app — not only internal tools",
            ],
            "rail_labels": ["Member Apps", "Claims Data", "AuthN/Z"],
            "cta": "If an app called your endpoints today — what fails first?",
            "footer_note": "Patient Access · FHIR · CMS Interoperability",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "steps": ["Checklist go-live", "FHIR endpoints", "Usable member apps"],
            "badge_labels": ["Patient Access", "FHIR", "Member", "Apps"],
            "accent_theme": "navy",
        }
    if "directory" in t:
        return {
            "image_layout": "hud_split",
            "image_title": "Provider Directory quality is the silent failure",
            "highlight": "Valid FHIR can still fail members",
            "left_label": "Looks Fine",
            "left_points": ["Valid resources", "Endpoints live", "Checklist passed"],
            "right_label": "Still Broken",
            "right_points": ["Stale phone/NPI", "Wrong network status", "No freshness owner"],
            "bullets": [],
            "cta": "Who owns freshness SLA when directory data drifts?",
            "footer_note": "Provider Directory · FHIR · CMS",
            "alert_label": "DATA QUALITY",
            "rail_labels": [],
            "steps": [],
            "badge_labels": ["Directory", "NPI", "Network", "SLA"],
            "accent_theme": "dark_green",
        }
    if (
        "profile" in t
        or "extension" in t
        or "resource modeling" in t
        or "uscdi" in t
        or "us core" in t
        or "azure" in t
        or "apim" in t
        or "api management" in t
    ):
        title = "Clean profiles beat one-off extensions"
        highlight = "Constrain first. Extend only when needed."
        bullets = [
            "Profiles + terminology bindings before custom extensions",
            "One-off extensions become consumer debt",
            "Ask: would a third-party app read this the same way?",
            "Clean contracts scale — clever extensions rarely do",
        ]
        if "uscdi" in t or "us core" in t:
            title, highlight = "USCDI & US Core", "Mapping is consumer protection"
            bullets = [
                "Stop every partner inventing a private dialect",
                "Must Support choices show up in real apps",
                "Map for the consumer — not warehouse comfort",
                "Know what breaks if apps only trust US Core",
            ]
        if "azure" in t or "apim" in t or "api management" in t:
            title, highlight = "Azure APIM for FHIR APIs", "Security and scale are product decisions"
            bullets = [
                "AuthZ boundaries and SMART scopes",
                "Throttling for noisy consumers",
                "Tracing across Patient Access / Directory / PA",
                "Policies reviewed with architecture — not last-mile",
            ]
        return {
            "image_layout": "hud_points",
            "alert_label": "KEY INSIGHTS",
            "image_title": title,
            "highlight": highlight,
            "bullets": bullets,
            "cta": "Ship clean contracts — not checklist theater.",
            "footer_note": "FHIR · CMS · Interoperability",
            "rail_labels": [],
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "steps": [],
            "badge_labels": ["FHIR", "CMS", "API", "Interop"],
            "accent_theme": "navy",
        }

    words = [w.strip("—,") for w in topic.replace("/", " ").split() if len(w) > 2][:4]
    while len(words) < 4:
        words += ["FHIR", "CMS", "API", "Interop"]
    return {
        "image_layout": "hud_alert",
        "alert_label": "HEALTH IT",
        "image_title": short,
        "highlight": "Connectivity ≠ coordination",
        "intro": "Standards create the contract. Architecture and ownership create the outcome.",
        "bullets": [
            f"Focus: {short}",
            "Architecture and ownership beat demos",
            "Data stewardship decides adoption",
            "Measure member and clinician outcomes",
        ],
        "rail_labels": words[:3],
        "cta": "Ship the operating model — not only the CapabilityStatement.",
        "footer_note": "FHIR · CMS · Interoperability · HealthIT",
        "left_label": "",
        "left_points": [],
        "right_label": "",
        "right_points": [],
        "steps": [],
        "badge_labels": words[:4],
        "accent_theme": "dark_green",
    }



def _fallback_post(topic: str) -> dict[str, Any]:
    profile = load_profile()
    name = profile.get("name", "Shiraj Momin")
    if topic in _FALLBACK_BODIES:
        hook, post = _FALLBACK_BODIES[topic]
    else:
        hook = "Interop wins come from operating model, not only standards."
        post = f"""Most FHIR programs do not fail on the standard — they fail on the operating model around it.

Today's focus: {topic}

When I work with payer and platform teams, the pattern is consistent: R4 resources get modeled, APIs go live, then Provider Directory data drifts, Patient Access responses feel incomplete, or Prior Auth (CRD/DTR/PAS) stalls because clinical and claims systems were never designed to share context.

Standards create the contract. Architecture, data stewardship, and delivery leadership determine whether members and clinicians actually feel the benefit.

If you are building CMS interoperability capability right now, what is the hardest part — the FHIR layer, the source systems, or the cross-team ownership?

#FHIR #CMSInteroperability #HealthIT #PriorAuthorization #HealthcareTechnology #APIManagement"""

    tags = [t for t in post.split() if t.startswith("#")]
    visual = _fallback_visual(topic, hook)
    return {
        "topic": topic,
        "hook": hook,
        "post_text": post.strip(),
        "hashtags": tags,
        "why_this_topic": f"Fallback draft for {name} on rotating topic bank.",
        **visual,
    }


def generate_post(topic: str | None = None, use_ai: bool = True) -> dict[str, Any]:
    chosen = pick_topic(topic)
    provider = env("AI_PROVIDER", "openai").lower()
    if not use_ai or provider in ("", "none"):
        return _fallback_post(chosen)

    system = load_prompt("linkedin_post_prompt.txt")
    profile = load_profile()
    user = json.dumps(
        {
            "author": {
                "name": profile.get("name"),
                "headline": profile.get("headline"),
                "summary": profile.get("summary"),
                "skills": profile.get("skills"),
                "linkedin": _profile_url(),
            },
            "today_topic_hint": chosen,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "style_notes": [
                "Match high-performing Health IT LinkedIn posts: sharp hook, short paragraphs.",
                "Prefer concrete FHIR/CMS language over generic digital transformation talk.",
            ],
        },
        indent=2,
    )

    result = call_llm(system, user)
    if not result or not (result.get("post_text") or "").strip():
        print("[linkedin] AI post failed — using fallback template")
        return _fallback_post(chosen)

    result.setdefault("topic", chosen)
    visual = _fallback_visual(result.get("topic") or chosen, result.get("hook") or chosen)
    for key, value in visual.items():
        if key == "image_layout" or not result.get(key):
            result[key] = value
    result["image_layout"] = visual.get("image_layout") or "hud_alert"
    print("[linkedin] AI post generated")
    return result


def email_post(post: dict[str, Any], image_path: Path) -> bool:
    body = f"""Your LinkedIn draft is ready.

Topic: {post.get('topic')}

1. Copy the text below into a new LinkedIn post
2. Upload the attached PNG as the post image
3. Publish

--- COPY BELOW ---

{post.get('post_text')}

--- END ---

Profile: {_profile_url()}
"""
    return send_text(
        subject="LinkedIn draft — FHIR / CMS interop",
        body=body,
        attachments=[image_path],
    )


def generate_and_deliver(*, use_ai: bool = True, send_email: bool = True, topic: str | None = None) -> None:
    import tempfile

    # Remove leftover local files from previous runs
    cleanup_runtime_files()

    post = generate_post(topic=topic, use_ai=use_ai)

    tmp_dir = Path(tempfile.mkdtemp(prefix="linkedin_agent_"))
    image_path = tmp_dir / "linkedin_post.png"
    create_post_image(post, image_path)

    print(f"[linkedin] Topic: {post.get('topic')}")
    print("---")
    try:
        print(post.get("post_text") or "")
    except UnicodeEncodeError:
        print((post.get("post_text") or "").encode("ascii", errors="replace").decode("ascii"))
    print("---")

    if send_email:
        ok = email_post(post, image_path)
        if ok:
            print("[linkedin] Email sent — use the email to post on LinkedIn")
        else:
            print("[linkedin] Email failed — check SMTP secrets / .env")

    # Always wipe temp + any leftover drafts/history after the run
    cleanup_runtime_files(extra_dirs=[tmp_dir])


def main() -> int:
    parser = argparse.ArgumentParser(description="LinkedIn Post Agent — email-only FHIR / CMS draft")
    parser.add_argument("--no-ai", action="store_true", help="Use template fallback")
    parser.add_argument("--no-email", action="store_true", help="Skip email (print only)")
    parser.add_argument("--topic", default="", help="Override today's topic")
    args = parser.parse_args()

    print("=" * 60)
    print("LinkedIn Post Agent")
    print("Output: email only (no local drafts or history)")
    print(f"Started: {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 60)

    generate_and_deliver(
        use_ai=not args.no_ai,
        send_email=not args.no_email,
        topic=args.topic or None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

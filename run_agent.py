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
from common import DATA_DIR, DRAFTS_DIR, ensure_dirs, env, load_profile, load_prompt
from linkedin_image import create_post_image, image_path_for_draft
from send_email import send_text

HISTORY_PATH = DATA_DIR / "post_history.json"

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


def _load_history() -> dict[str, Any]:
    if not HISTORY_PATH.exists():
        return {"used_topics": [], "posts": []}
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"used_topics": [], "posts": []}


def _save_history(history: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def pick_topic(override: str | None = None) -> str:
    if override:
        return override.strip()
    history = _load_history()
    used = set(history.get("used_topics") or [])
    for topic in TOPIC_BANK:
        if topic not in used:
            return topic
    history["used_topics"] = []
    _save_history(history)
    return TOPIC_BANK[0]


def _profile_url() -> str:
    return load_profile().get("linkedin_url") or "https://www.linkedin.com/in/shiraj-momin-25610232/"


def _fallback_visual(topic: str, hook: str) -> dict[str, Any]:
    """Unique infographic brief per topic — never reuse one generic card set."""
    t = topic.lower()
    short = hook if len(hook) <= 56 else " ".join(hook.split()[:8])

    if "edi" in t or "837" in t or "834" in t:
        return {
            "image_layout": "split_compare",
            "accent_theme": "green_split",
            "image_title": "EDI roots → FHIR APIs",
            "image_subtitle": "Keep the wisdom. Leave the coupling.",
            "left_label": "EDI Era",
            "left_points": ["Batch windows", "File coupling", "Partner-specific maps"],
            "right_label": "FHIR Era",
            "right_points": ["Interactive APIs", "Reusable contracts", "Member-ready access"],
            "badge_labels": ["EDI", "X12", "FHIR", "API"],
            "steps": [],
            "bullets": [],
        }
    if "profile" in t or "extension" in t or "resource modeling" in t:
        return {
            "image_layout": "key_points",
            "accent_theme": "teal",
            "image_title": "Clean FHIR profiles",
            "image_subtitle": "Constrain first. Extend only when needed.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Profile", "Binding", "Extension", "Contract"],
            "steps": [],
            "bullets": [
                "Profiles + terminology bindings before custom extensions",
                "One-off extensions become consumer debt",
                "Ask: would a third-party app read this the same way?",
                "Clean contracts scale — clever extensions rarely do",
            ],
        }
    if "patient access" in t:
        return {
            "image_layout": "before_after",
            "accent_theme": "teal",
            "image_title": "Patient Access API",
            "image_subtitle": "Compliance ≠ member experience",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Member", "EOB", "Auth", "Apps"],
            "steps": ["Checklist go-live", "FHIR endpoints", "Usable member apps"],
            "bullets": [],
        }
    if "directory" in t:
        return {
            "image_layout": "split_compare",
            "accent_theme": "green_split",
            "image_title": "Provider Directory quality",
            "image_subtitle": "Valid FHIR can still fail members.",
            "left_label": "Looks Fine",
            "left_points": ["Valid resources", "Endpoints live", "Checklist passed"],
            "right_label": "Still Broken",
            "right_points": ["Stale phone/NPI", "Wrong network status", "No freshness owner"],
            "badge_labels": ["NPI", "Network", "Freshness", "SLA"],
            "steps": [],
            "bullets": [],
        }
    if "crd" in t or "coverage requirement" in t:
        return {
            "image_layout": "workflow",
            "accent_theme": "purple",
            "image_title": "CMS-0057-F · CRD",
            "image_subtitle": "Surface coverage rules at decision time.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["CRD", "CDS Hooks", "Coverage", "EHR"],
            "steps": ["Order context", "CDS Hook", "Coverage rules", "Clinician sees ask"],
            "bullets": [],
        }
    if "dtr" in t:
        return {
            "image_layout": "key_points",
            "accent_theme": "orange",
            "image_title": "CMS-0057-F · DTR",
            "image_subtitle": "Questionnaires decide adoption.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["DTR", "Questionnaire", "Pre-fill", "Clinic"],
            "steps": [],
            "bullets": [
                "Vague templates create click-burden",
                "Pre-populate from FHIR clinical resources",
                "Make 'why we need this' explicit",
                "Fix the questionnaire library before the transport",
            ],
        }
    if "pas" in t:
        return {
            "image_layout": "dark_tech",
            "accent_theme": "dark_green",
            "image_title": short,
            "image_subtitle": "A valid Bundle is still a multi-resource transaction.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Claim", "Coverage", "Request", "Actors"],
            "hub_label": "PAS",
            "steps": [],
            "bullets": [
                "Claim — administrative backbone",
                "ServiceRequest / DeviceRequest — clinical intent",
                "Condition & Observation — medical necessity",
                "Coverage — enrollment link",
                "Practitioner & Organization — actors",
            ],
        }
    if "0057" in t or "prior auth" in t or "prior-auth" in t:
        return {
            "image_layout": "workflow",
            "accent_theme": "purple",
            "image_title": "Prior Auth on FHIR",
            "image_subtitle": "CRD → DTR → PAS as one operating model.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["CRD", "DTR", "PAS", "FHIR"],
            "steps": ["Provider initiates", "Send via FHIR", "Payer validates", "Decision returned", "Provider receives"],
            "bullets": [],
        }
    if "bulk" in t or "$export" in t or "export" in t:
        return {
            "image_layout": "workflow",
            "accent_theme": "blue",
            "image_title": "FHIR Bulk Data / $export",
            "image_subtitle": "Ops design before the happy-path demo.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["$export", "NDJSON", "Retry", "Audit"],
            "steps": ["Kick off", "Poll status", "Download NDJSON", "Reconcile", "Alert"],
            "bullets": [],
        }
    if "azure" in t or "apim" in t or "api management" in t:
        return {
            "image_layout": "key_points",
            "accent_theme": "blue",
            "image_title": "Azure APIM for FHIR",
            "image_subtitle": "Security and scale are product decisions.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["APIM", "AuthZ", "Throttle", "Trace"],
            "steps": [],
            "bullets": [
                "AuthZ boundaries and SMART scopes",
                "Throttling for noisy consumers",
                "Tracing across Patient Access / Directory / PA",
                "Policies reviewed with architecture — not last-mile",
            ],
        }
    if "smart" in t:
        return {
            "image_layout": "dark_tech",
            "accent_theme": "navy",
            "image_title": "SMART on FHIR launch",
            "image_subtitle": "Security is an architecture choice.",
            "hub_label": "SMART",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Launch", "Token", "Scope", "Context"],
            "steps": [],
            "bullets": [
                "Redirect hygiene and launch context integrity",
                "Token lifetime and scope discipline",
                "EHR vs standalone threat models differ",
                "Test context spoofing before partner go-live",
            ],
        }
    if "medicare" in t or "commercial" in t:
        return {
            "image_layout": "split_compare",
            "accent_theme": "green_split",
            "image_title": "Same FHIR. Different constraints.",
            "image_subtitle": "Medicare vs commercial operating models.",
            "left_label": "Medicare lines",
            "left_points": ["Coverage constructs", "Network rules", "Identity resolution"],
            "right_label": "Commercial lines",
            "right_points": ["Product variation", "Partner SLAs", "Claims semantics"],
            "badge_labels": ["Medicare", "Commercial", "FHIR", "Coverage"],
            "steps": [],
            "bullets": [],
        }
    if "leadership" in t or "sequencing" in t:
        return {
            "image_layout": "before_after",
            "accent_theme": "orange",
            "image_title": "Sequence the risk",
            "image_subtitle": "Interop fails on delivery order, not standards.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Directory", "Access", "Prior Auth", "Own"],
            "steps": ["Directory quality", "Identity & consent", "Patient Access", "Prior Auth APIs"],
            "bullets": [],
        }
    if "ai " in t or "assistant" in t or t.startswith("how ai"):
        return {
            "image_layout": "key_points",
            "accent_theme": "purple",
            "image_title": "AI helps. Humans own contracts.",
            "image_subtitle": "Accelerate drafts. Gate production semantics.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["AI", "Draft", "Govern", "Sign-off"],
            "steps": [],
            "bullets": [
                "AI can draft CapabilityStatements and mappings faster",
                "Humans own when an extension is justified",
                "Questionnaire UX still needs clinical judgment",
                "Keep an architect gate on production sign-off",
            ],
        }
    if "uscdi" in t or "us core" in t:
        return {
            "image_layout": "key_points",
            "accent_theme": "teal",
            "image_title": "USCDI & US Core",
            "image_subtitle": "Mapping is consumer protection.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["USCDI", "US Core", "Must Support", "Terms"],
            "steps": [],
            "bullets": [
                "Stop every partner inventing a private dialect",
                "Must Support choices show up in real apps",
                "Map for the consumer — not warehouse comfort",
                "Know what breaks if apps only trust US Core",
            ],
        }
    if "test" in t or "synthetic" in t:
        return {
            "image_layout": "workflow",
            "accent_theme": "orange",
            "image_title": "Interop testing",
            "image_subtitle": "Negative paths catch the real bugs.",
            "left_label": "",
            "left_points": [],
            "right_label": "",
            "right_points": [],
            "badge_labels": ["Synthetic", "Negative", "Contract", "CI"],
            "steps": ["Happy path", "Expired token", "Empty Bundle", "Conflict IDs", "Pended PA"],
            "bullets": [],
        }

    # Last resort: still unique via topic hash (layout + theme + badges from topic words)
    layouts = ["title_network", "key_points", "before_after", "dark_tech"]
    themes = ["blue", "teal", "navy", "orange", "purple"]
    h = abs(hash(topic)) 
    layout = layouts[h % len(layouts)]
    theme = themes[(h // 3) % len(themes)]
    words = [w.strip("—,") for w in topic.replace("/", " ").split() if len(w) > 2][:4]
    while len(words) < 4:
        words.append("FHIR")
    base = {
        "image_layout": layout,
        "accent_theme": theme,
        "image_title": short,
        "image_subtitle": "Standards create the contract. Delivery creates the outcome.",
        "left_label": words[0][:16],
        "left_points": ["Fragile integrations", "Hidden data debt", "Checklist theater"],
        "right_label": words[1][:16],
        "right_points": ["Reusable APIs", "Owned data quality", "Member impact"],
        "badge_labels": [w[:14] for w in words],
        "hub_label": "FHIR",
        "steps": ["Design", "Contract", "Test", "Operate", "Improve"],
        "bullets": [
            f"Focus: {short}",
            "Architecture and ownership beat demos",
            "Data stewardship decides adoption",
            "Measure member/clinician outcomes",
        ],
    }
    return base



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
    history = _load_history()
    recent = [p.get("topic") for p in (history.get("posts") or [])[-5:]]
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
            "recent_topics_to_avoid": recent,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "style_notes": [
                "Match high-performing Health IT LinkedIn posts: sharp hook, short paragraphs, infographic-ready visual fields.",
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
    # Fill missing visual fields from topic heuristics
    visual = _fallback_visual(result.get("topic") or chosen, result.get("hook") or chosen)
    for key, value in visual.items():
        if not result.get(key):
            result[key] = value
    print("[linkedin] AI post generated")
    return result


def save_post(post: dict[str, Any]) -> tuple[Path, Path]:
    ensure_dirs()
    stamp = datetime.now().strftime("%Y-%m-%d")
    path = DRAFTS_DIR / f"{stamp}.md"
    if path.exists():
        path = DRAFTS_DIR / f"{stamp}_{datetime.now().strftime('%H%M%S')}.md"

    image_path = image_path_for_draft(path)
    create_post_image(post, image_path)

    tags = " ".join(post.get("hashtags") or [])
    body = f"""# LinkedIn draft — {stamp}

**Topic:** {post.get('topic')}
**Hook:** {post.get('hook')}
**Why:** {post.get('why_this_topic')}
**Image:** {image_path.name}
**Layout:** {post.get('image_layout')}

---

## Copy & paste to LinkedIn

{post.get('post_text')}

---

## Image (attach on LinkedIn)

Upload this file with your post: `{image_path}`

Suggested tags: {tags}
Profile: {_profile_url()}
"""
    path.write_text(body, encoding="utf-8")

    history = _load_history()
    used = list(history.get("used_topics") or [])
    topic = post.get("topic") or ""
    if topic and topic not in used:
        used.append(topic)
    posts = list(history.get("posts") or [])
    posts.append(
        {
            "date": stamp,
            "topic": topic,
            "path": str(path),
            "image": str(image_path),
            "hook": post.get("hook"),
        }
    )
    history["used_topics"] = used
    history["posts"] = posts[-90:]
    _save_history(history)
    return path, image_path


def email_post(post: dict[str, Any], path: Path, image_path: Path) -> bool:
    body = f"""Your LinkedIn draft for today is ready.

Topic: {post.get('topic')}
Post file: {path}
Image file: {image_path}  (also attached to this email)

1. Copy the text below into a new LinkedIn post
2. Upload the attached PNG as the post image
3. Publish

--- COPY BELOW ---

{post.get('post_text')}

--- END ---

Paste into LinkedIn when ready:
{_profile_url()}
"""
    return send_text(
        subject="Daily draft — FHIR / CMS interop",
        body=body,
        attachments=[image_path],
    )


def generate_and_deliver(*, use_ai: bool = True, send_email: bool = True, topic: str | None = None) -> Path:
    post = generate_post(topic=topic, use_ai=use_ai)
    path, image_path = save_post(post)
    print(f"[linkedin] Draft written: {path}")
    print(f"[linkedin] Image written: {image_path}")
    print("---")
    try:
        print(post.get("post_text") or "")
    except UnicodeEncodeError:
        print((post.get("post_text") or "").encode("ascii", errors="replace").decode("ascii"))
    print("---")
    if send_email:
        email_post(post, path, image_path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="LinkedIn Post Agent — daily FHIR / CMS draft")
    parser.add_argument("--no-ai", action="store_true", help="Use template fallback")
    parser.add_argument("--no-email", action="store_true", help="Skip email")
    parser.add_argument("--topic", default="", help="Override today's topic")
    args = parser.parse_args()

    print("=" * 60)
    print("LinkedIn Post Agent")
    print("Topics: FHIR · CMS interoperability · health tech")
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

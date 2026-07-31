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


# Each pack has unique image_layout + accent_theme so visuals do not repeat.
CONTENT_LIBRARY: list[dict[str, Any]] = [
    {
        "id": "compliance",
        "topic": "CMS-0057-F compliance — modernize healthcare data exchange by 2027",
        "hook": "CMS-0057-F is more than a compliance requirement.",
        "post_text": """CMS-0057-F is more than a compliance requirement—it's an opportunity to modernize healthcare data exchange.

Patient Access, Provider Access, Payer-to-Payer, and Prior Authorization APIs are reshaping interoperability.

Is your organization ready for 2027?

#CMS0057F #FHIR #HealthcareIT #Interoperability #HealthTech""",
        "image_layout": "hud_pillars",
        "accent_theme": "cyan",
        "alert_label": "COMPLIANCE FOCUS",
        "image_title": "CMS-0057-F is an opportunity",
        "highlight": "Ready for 2027?",
        "intro": "Four APIs reshaping healthcare interoperability.",
        "bullets": ["Patient Access", "Provider Access", "Payer-to-Payer", "Prior Authorization"],
        "badge_labels": ["CMS-0057-F", "FHIR", "APIs", "2027"],
        "cta": "Is your organization ready for 2027?",
        "footer_note": "CMS-0057-F · FHIR · Interoperability",
    },
    {
        "id": "prior_auth",
        "topic": "Prior Authorization with CRD, DTR, and PAS",
        "hook": "Prior Authorization doesn't have to be a manual process.",
        "post_text": """Prior Authorization doesn't have to be a manual process.

CRD identifies requirements.
DTR gathers documentation.
PAS submits the authorization.

FHIR is helping healthcare move toward real-time decisions.

#PriorAuthorization #FHIR #DaVinci #HealthcareInnovation #CMS0057F""",
        "image_layout": "hud_workflow",
        "accent_theme": "lime",
        "alert_label": "PRIOR AUTH",
        "image_title": "CRD → DTR → PAS",
        "highlight": "From manual process to real-time decisions",
        "steps": [
            "CRD identifies requirements",
            "DTR gathers documentation",
            "PAS submits the authorization",
        ],
        "bullets": [
            "CRD identifies requirements",
            "DTR gathers documentation",
            "PAS submits the authorization",
        ],
        "badge_labels": ["CRD", "DTR", "PAS", "Da Vinci"],
        "cta": "FHIR moves healthcare toward real-time decisions.",
        "footer_note": "Prior Auth · Da Vinci · CMS-0057-F",
    },
    {
        "id": "dotnet",
        "topic": ".NET 10 + Healthcare FHIR APIs",
        "hook": "Building healthcare APIs requires performance, security, and scalability.",
        "post_text": """Building healthcare APIs requires performance, security, and scalability.

.NET 10 continues to strengthen the foundation for modern FHIR-based healthcare solutions.

What feature are you most excited about?

#DotNet10 #HealthcareIT #FHIR #CloudArchitecture #HealthTech""",
        "image_layout": "hud_hero",
        "accent_theme": "sky",
        "alert_label": ".NET 10",
        "image_title": ".NET 10 for FHIR healthcare APIs",
        "highlight": "Performance · Security · Scalability",
        "bullets": ["Performance for FHIR workloads", "Security for healthcare data", "Scalability for cloud APIs"],
        "badge_labels": [".NET 10", "FHIR", "Cloud", "APIs"],
        "cta": "What feature are you most excited about?",
        "footer_note": ".NET 10 · Healthcare IT · FHIR",
    },
    {
        "id": "patient_access",
        "topic": "Patient Access API — digital access to healthcare information",
        "hook": "Patients expect digital access to their healthcare information.",
        "post_text": """Patients expect digital access to their healthcare information.

FHIR-based Patient Access APIs are helping make that expectation a reality.

Better access leads to better engagement.

#PatientAccessAPI #FHIR #CMS0057F #DigitalHealth #Healthcare""",
        "image_layout": "hud_points",
        "accent_theme": "teal",
        "alert_label": "PATIENT ACCESS",
        "image_title": "Patients expect digital access",
        "highlight": "Better access → better engagement",
        "bullets": [
            "Members expect app-ready health data",
            "FHIR Patient Access APIs open the door",
            "Complete payloads build trust",
            "Engagement follows usable access",
        ],
        "badge_labels": ["Patient Access", "FHIR", "Members", "Apps"],
        "cta": "Better access leads to better engagement.",
        "footer_note": "Patient Access · FHIR · CMS-0057-F",
    },
    {
        "id": "provider_directory",
        "topic": "Provider Directory — accurate searchable provider data",
        "hook": "Accurate provider data is essential for care coordination.",
        "post_text": """Accurate provider data is essential for care coordination.

FHIR Provider Directory APIs help deliver standardized, searchable provider information across the healthcare ecosystem.

#ProviderDirectory #FHIR #HealthcareData #Interoperability #HealthIT""",
        "image_layout": "hud_grid",
        "accent_theme": "mint",
        "alert_label": "DIRECTORY",
        "image_title": "Accurate provider data",
        "highlight": "Standardized · Searchable · Trusted",
        "bullets": ["Standardized FHIR resources", "Searchable across networks", "Fresh NPI & locations", "Trusted care coordination"],
        "badge_labels": ["Directory", "NPI", "FHIR", "Search"],
        "cta": "Care coordination starts with clean directory data.",
        "footer_note": "Provider Directory · FHIR · HealthIT",
        "left_label": "Looks Fine",
        "left_points": ["Valid FHIR", "Endpoints live", "Checklist passed"],
        "right_label": "Still Broken",
        "right_points": ["Stale phone/NPI", "Wrong network", "No freshness owner"],
    },
    {
        "id": "payer_to_payer",
        "topic": "Payer-to-Payer Data Exchange for continuity of care",
        "hook": "Healthcare data shouldn't stop moving when a member changes plans.",
        "post_text": """Healthcare data shouldn't stop moving when a member changes plans.

Payer-to-Payer Data Exchange helps ensure continuity of care and a better member experience.

#PayerToPayer #FHIR #CMS0057F #HealthcareInteroperability #DigitalTransformation""",
        "image_layout": "hud_stack",
        "accent_theme": "amber",
        "alert_label": "P2P EXCHANGE",
        "image_title": "Data shouldn't stop at plan change",
        "highlight": "Continuity of care across payers",
        "steps": [
            "Member changes health plan",
            "Payer-to-Payer data exchange",
            "Clinical & claims continuity",
            "Better member experience",
        ],
        "bullets": [
            "Member changes health plan",
            "Payer-to-Payer data exchange",
            "Clinical & claims continuity",
            "Better member experience",
        ],
        "badge_labels": ["P2P", "FHIR", "CMS", "Members"],
        "cta": "Continuity of care starts with portable data.",
        "footer_note": "Payer-to-Payer · FHIR · CMS-0057-F",
    },
    {
        "id": "cdex",
        "topic": "CDex — clinical data exchange for modern workflows",
        "hook": "Clinical data exchange is becoming critical to modern healthcare workflows.",
        "post_text": """Clinical data exchange is becoming a critical part of modern healthcare workflows.

CDex enables the secure exchange of clinical documents, reducing delays and improving collaboration.

#CDex #FHIR #ClinicalDataExchange #HealthcareIT #DaVinci""",
        "image_layout": "hud_split",
        "accent_theme": "emerald",
        "alert_label": "CDex",
        "image_title": "Clinical data without the delay",
        "highlight": "Secure document exchange",
        "left_label": "Without CDex",
        "left_points": ["Fax / portal chase", "Delayed documents", "Broken collaboration"],
        "right_label": "With CDex",
        "right_points": ["Secure FHIR exchange", "Faster document flow", "Better collaboration"],
        "bullets": ["Secure clinical documents", "Fewer delays", "Stronger collaboration"],
        "badge_labels": ["CDex", "Da Vinci", "FHIR", "Docs"],
        "cta": "Reduce delays. Improve clinical collaboration.",
        "footer_note": "CDex · Da Vinci · Clinical Data Exchange",
    },
    {
        "id": "api_security",
        "topic": "API Security — OAuth 2.0 and SMART on FHIR",
        "hook": "Interoperability starts with trust.",
        "post_text": """Interoperability starts with trust.

OAuth 2.0, SMART on FHIR, and secure API design are key to protecting healthcare data while enabling innovation.

#APISecurity #SMARTonFHIR #HealthcareSecurity #FHIR #HealthTech""",
        "image_layout": "hud_security",
        "accent_theme": "coral",
        "alert_label": "SECURITY",
        "image_title": "Interoperability starts with trust",
        "highlight": "Protect data. Enable innovation.",
        "bullets": ["OAuth 2.0", "SMART on FHIR", "Secure API design", "Least-privilege scopes"],
        "badge_labels": ["OAuth", "SMART", "FHIR", "Trust"],
        "cta": "Trust is the first interoperability requirement.",
        "footer_note": "API Security · SMART on FHIR · HealthTech",
    },
    {
        "id": "cds_hooks",
        "topic": "CDS Hooks — coverage guidance in the clinical workflow",
        "hook": "What if providers could receive coverage guidance during their workflow?",
        "post_text": """What if providers could receive coverage guidance during their workflow?

CDS Hooks brings real-time decision support directly into the clinical experience.

#CDSHooks #FHIR #HealthcareInnovation #DigitalHealth #HealthIT""",
        "image_layout": "hud_alert",
        "accent_theme": "navy",
        "alert_label": "CDS HOOKS",
        "image_title": "Coverage guidance in the workflow",
        "highlight": "Real-time clinical decision support",
        "intro": "Bring coverage rules to the point of care — not after denial.",
        "bullets": [
            "Hook into the clinical workflow",
            "Surface coverage requirements early",
            "Reduce after-the-fact denials",
            "Keep guidance actionable in seconds",
        ],
        "badge_labels": ["CDS Hooks", "CRD", "FHIR", "EHR"],
        "cta": "Decision support belongs in the clinical moment.",
        "footer_note": "CDS Hooks · FHIR · Digital Health",
    },
    {
        "id": "future",
        "topic": "Future of healthcare — connected, automated, interoperable",
        "hook": "The future of healthcare is connected, automated, and interoperable.",
        "post_text": """The future of healthcare is connected, automated, and interoperable.

FHIR standards, cloud platforms, AI, and modern APIs are accelerating that transformation.

Where do you see the biggest opportunity?

#FHIR #HealthTech #HealthcareInnovation #DigitalTransformation #CMS0057F""",
        "image_layout": "hud_quote",
        "accent_theme": "steel",
        "alert_label": "FUTURE",
        "image_title": "Where do you see the biggest opportunity?",
        "highlight": "Connected · Automated · Interoperable",
        "bullets": ["FHIR standards", "Cloud platforms", "AI assistants", "Modern APIs"],
        "badge_labels": ["FHIR", "Cloud", "AI", "APIs"],
        "cta": "Connected. Automated. Interoperable.",
        "footer_note": "FHIR · HealthTech · Digital Transformation",
    },
]

TOPIC_BANK = [c["topic"] for c in CONTENT_LIBRARY]


def pick_topic(override: str | None = None) -> str:
    if override:
        return override.strip()
    import random

    return random.choice(TOPIC_BANK)


def _profile_url() -> str:
    return load_profile().get("linkedin_url") or "https://www.linkedin.com/in/shiraj-momin-25610232/"


def _pack_for_topic(topic: str) -> dict[str, Any] | None:
    t = topic.lower()
    for pack in CONTENT_LIBRARY:
        if pack["topic"].lower() == t:
            return pack
    # keyword match for AI / override topics
    rules = [
        ("dotnet", "dotnet"),
        (".net", "dotnet"),
        ("prior auth", "prior_auth"),
        ("crd", "prior_auth"),
        ("dtr", "prior_auth"),
        ("pas", "prior_auth"),
        ("patient access", "patient_access"),
        ("directory", "provider_directory"),
        ("payer-to-payer", "payer_to_payer"),
        ("payer to payer", "payer_to_payer"),
        ("cdex", "cdex"),
        ("smart", "api_security"),
        ("oauth", "api_security"),
        ("security", "api_security"),
        ("cds hook", "cds_hooks"),
        ("cds hooks", "cds_hooks"),
        ("0057", "compliance"),
        ("compliance", "compliance"),
        ("future", "future"),
    ]
    for needle, pack_id in rules:
        if needle in t:
            return next(p for p in CONTENT_LIBRARY if p["id"] == pack_id)
    return None


def _visual_from_pack(pack: dict[str, Any]) -> dict[str, Any]:
    skip = {"id", "topic", "hook", "post_text"}
    return {k: v for k, v in pack.items() if k not in skip}


def _fallback_visual(topic: str, hook: str) -> dict[str, Any]:
    pack = _pack_for_topic(topic)
    if pack:
        return _visual_from_pack(pack)
    # Unknown topic → rotate unique layout by hash so images still vary
    import hashlib

    layouts = [
        "hud_alert",
        "hud_workflow",
        "hud_pillars",
        "hud_quote",
        "hud_split",
        "hud_points",
        "hud_grid",
        "hud_stack",
        "hud_security",
        "hud_hero",
    ]
    themes = ["lime", "cyan", "teal", "amber", "coral", "steel", "mint", "sky", "navy", "emerald"]
    idx = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16)
    short = hook if len(hook) <= 56 else " ".join(hook.split()[:8])
    return {
        "image_layout": layouts[idx % len(layouts)],
        "accent_theme": themes[(idx // 3) % len(themes)],
        "alert_label": "HEALTH IT",
        "image_title": short,
        "highlight": "Connected · Automated · Interoperable",
        "bullets": [short, "Architecture and ownership beat demos", "Data stewardship decides adoption", "Measure real outcomes"],
        "badge_labels": ["FHIR", "CMS", "API", "Interop"],
        "cta": "Where do you see the biggest opportunity?",
        "footer_note": "FHIR · CMS · Interoperability · HealthIT",
        "steps": [],
        "left_label": "",
        "left_points": [],
        "right_label": "",
        "right_points": [],
    }


def _fallback_post(topic: str) -> dict[str, Any]:
    profile = load_profile()
    name = profile.get("name", "Shiraj Momin")
    pack = _pack_for_topic(topic)
    if pack:
        hook = pack["hook"]
        post = pack["post_text"]
        visual = _visual_from_pack(pack)
    else:
        hook = "Interop wins come from operating model, not only standards."
        post = f"""Most FHIR programs do not fail on the standard — they fail on the operating model around it.

Today's focus: {topic}

Standards create the contract. Architecture, data stewardship, and delivery leadership determine whether members and clinicians actually feel the benefit.

Where do you see the biggest opportunity?

#FHIR #CMSInteroperability #HealthIT #HealthcareTechnology #HealthTech"""
        visual = _fallback_visual(topic, hook)

    tags = [t for t in post.split() if t.startswith("#")]
    return {
        "topic": topic,
        "hook": hook,
        "post_text": post.strip(),
        "hashtags": tags,
        "why_this_topic": f"Content pack for {name}.",
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
    # Always apply unique pack visuals so images do not collapse to one layout
    visual = _fallback_visual(result.get("topic") or chosen, result.get("hook") or chosen)
    for key, value in visual.items():
        if key in ("image_layout", "accent_theme") or not result.get(key):
            result[key] = value
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

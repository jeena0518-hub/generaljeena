#!/usr/bin/env python3
"""
Jeena's Unified Command Center Bot
Sends morning briefings, evening pushes, and sneaky GMAT facts to Telegram.
Usage: python main.py [morning|evening|sneak]
"""

import anthropic
import requests
import feedparser
import json
import os
import sys
import random
from datetime import datetime, timezone

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_telegram(message: str) -> None:
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def fetch_rss_headlines(feeds: list, max_per_feed: int = 3) -> list:
    """Fetch headlines from a list of RSS feed URLs."""
    headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                if title:
                    headlines.append(f"• {title}")
        except Exception:
            pass
    return headlines


def get_ttp_topic() -> str:
    """Get today's TTP study topic from schedule.json."""
    today = datetime.now().strftime("%Y-%m-%d")
    schedule_path = os.path.join(os.path.dirname(__file__), "schedule.json")
    try:
        with open(schedule_path) as f:
            schedule = json.load(f)
        topic = schedule.get(today)
        if topic:
            return topic
    except Exception:
        pass
    # Fallback: smart default
    return (
        "General GMAT review — revisit your mistake log and drill your weakest "
        "problem type. Focus on quality over quantity today."
    )


# ── Message Modes ─────────────────────────────────────────────────────────────
def morning_briefing() -> None:
    """5am PT — News briefing + GMAT mission + morning fuel."""

    web3_headlines = fetch_rss_headlines([
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://cointelegraph.com/rss",
    ])
    ai_tech_headlines = fetch_rss_headlines([
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ])
    world_headlines = fetch_rss_headlines([
        "https://feeds.reuters.com/reuters/topNews",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ])

    ttp_topic = get_ttp_topic()
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    # Days until April 12 GMAT
    gmat_date = datetime(2026, 4, 12)
    days_left = (gmat_date - datetime.now()).days
    gmat_countdown = f"⏳ *{days_left} days until your GMAT on April 12.*" if days_left > 0 else "🎯 *GMAT day is here — you've got this!*"

    prompt = f"""You are Jeena's personal AI coach delivering her daily morning briefing. Today is {today_str}.

Here are today's latest headlines pulled from live RSS feeds:

**WEB3 & CRYPTO:**
{chr(10).join(web3_headlines) if web3_headlines else "• Crypto markets continue to evolve globally."}

**AI & TECH:**
{chr(10).join(ai_tech_headlines) if ai_tech_headlines else "• AI developments continue accelerating across industries."}

**WORLD:**
{chr(10).join(world_headlines) if world_headlines else "• Global developments continue across markets and geopolitics."}

**TODAY'S TTP STUDY FOCUS:**
{ttp_topic}

Write Jeena's morning briefing in exactly this format:

{gmat_countdown}

📰 *MORNING BRIEFING*
Write 4-5 punchy bullet points summarizing the most interesting and relevant headlines above. Be specific — use the actual topics from the headlines. Include anything that could affect crypto, AI, or markets.

📚 *TODAY'S GMAT MISSION*
Based on the TTP topic above, give Jeena a specific, tactical study plan for today. Include 1-2 concrete tips specific to the exact topic she's studying. Under 5 sentences. Make her feel like she has a clear target.

🔥 *MORNING FUEL*
A powerful, direct motivational message for Jeena. She's grinding the GMAT while working full time. She chose this hard path on purpose. Speak to her fire. Reference the countdown to April 12 if relevant. 3-4 sentences — no clichés, no generic advice. Make it personal and raw.

Use Telegram markdown. Total message under 550 words."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1100,
        messages=[{"role": "user", "content": prompt}]
    )
    send_telegram(response.content[0].text)


def evening_push() -> None:
    """7pm PT — Evening motivation + why reminder + push harder."""

    ttp_topic = get_ttp_topic()
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    gmat_date = datetime(2026, 4, 12)
    days_left = (gmat_date - datetime.now()).days
    gmat_countdown = f"⏳ *{days_left} days until your GMAT on April 12.*" if days_left > 0 else "🎯 *GMAT day is here — show up.*"

    prompt = f"""You are Jeena's personal AI coach checking in at the end of the day. Today is {today_str}.

Today's GMAT focus was: {ttp_topic}

Write Jeena's evening check-in in exactly this format:

{gmat_countdown}

💪 *EVENING CHECK-IN*
A direct, no-BS message that acknowledges how hard today probably was. She worked a full day AND is grinding for the GMAT. Name the difficulty. Don't sugarcoat it. Then push her harder. 3-4 sentences.

🎯 *REMEMBER WHAT THIS IS FOR*
Tell her what getting a great GMAT score actually means for her life. Business school. New doors. The version of herself she's building right now. Make it visceral and real. 2-3 sentences.

🚀 *TONIGHT'S EDGE*
One specific, actionable thing she can do tonight to get ahead. Make it directly relevant to her current TTP topic. Something small but meaningful — 20-30 minutes max. 2 sentences.

Be raw, direct, real. No fluff. Speak like a coach who believes in her more than she believes in herself. Telegram markdown. Under 280 words."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    send_telegram(response.content[0].text)


def gmat_sneak() -> None:
    """Sporadic workday — Trending culture opener + hidden GMAT fact."""

    # Fetch trending entertainment headlines
    ent_headlines = fetch_rss_headlines([
        "https://variety.com/feed/",
        "https://deadline.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
        "https://collider.com/feed/",
    ], max_per_feed=4)

    # GMAT concept bank — rotates randomly
    gmat_concepts = [
        ("Rate Problems", "distance = rate × time. When two things move toward each other, add their rates. When moving apart, still add. Classic trap: forgetting to add rates."),
        ("Work Problems", "combined rate = 1/a + 1/b where a and b are individual completion times. If A does a job in 3 hrs and B in 6 hrs, together: 1/3 + 1/6 = 1/2, so 2 hours total."),
        ("Percent Change", "formula is (new − old) / old × 100. A common trap: a 20% increase followed by a 20% decrease does NOT return to the original. You end up at 96%."),
        ("Data Sufficiency", "you're not solving — you're asking 'is there enough info to solve?' Always check whether the two statements together give exactly ONE answer, not just an answer."),
        ("Critical Reasoning: Strengthen", "to strengthen an argument, find what fills the gap between the premise and the conclusion. The correct answer often addresses an unstated assumption."),
        ("Critical Reasoning: Weaken", "to weaken, attack the assumption. Find what makes the conclusion less likely to follow from the premises. Extreme language in answer choices is usually a trap."),
        ("Sentence Correction: Subject-Verb Agreement", "find the true subject — ignore prepositional phrases. 'The results of the study was...' is wrong. 'Study' is not the subject. 'Results' is. Use 'were.'"),
        ("Overlapping Sets", "use a matrix or Venn diagram. Total = Group A + Group B − Both + Neither. Always check if 'neither' is in play — it's a common trap omission."),
        ("Number Properties", "even × anything = even. odd × odd = odd. even ± odd = odd. If you see 'must be even,' test even and odd values — don't assume."),
        ("Inequalities", "flip the inequality sign ONLY when multiplying or dividing by a negative number. Adding/subtracting never flips it. Easy point if you remember this."),
        ("Ratios", "set up a ratio equation: a/b = c/d. Cross multiply to solve. When a ratio is given as 2:3, the actual values could be 2x and 3x for any positive x."),
        ("Reading Comprehension: Primary Purpose", "the primary purpose is almost never just 'to describe.' Look for verbs: to argue, to challenge, to compare, to explain. Read the first and last paragraph carefully."),
        ("Probability", "P(A and B) = P(A) × P(B) only if events are independent. P(A or B) = P(A) + P(B) − P(A and B). Don't add when you should multiply."),
        ("Bold Face CR", "identify the role of each bold statement. Ask: is it a conclusion, a premise, or an objection? The answer choices describe the logical relationship between the two bold parts."),
        ("Combinatorics", "permutations = order matters: n!/(n−r)!. Combinations = order doesn't matter: n!/r!(n−r)!. 'Choose' = combinations. 'Arrange' = permutations."),
        ("Inference Questions (CR)", "the correct inference MUST be true based only on the passage. It can't go beyond the information given. If it requires outside knowledge, it's wrong."),
        ("Logical Flaw", "identify the flawed reasoning pattern: circular logic, false cause, false analogy, sampling error. Name it before looking at answer choices."),
        ("Evaluate the Argument (CR)", "find the answer that, depending on the answer, would either strengthen OR weaken the argument. If knowing X doesn't change whether the argument holds, it's wrong."),
        ("Statistics: Mean vs Median", "mean is sensitive to outliers; median is not. If the question asks about the 'typical' value in a skewed dataset, median is usually more informative. Know which is which."),
        ("Modifiers (SC)", "a modifier must be placed directly next to the word it modifies. 'Running down the street, the rain soaked her' is wrong — the rain wasn't running. Watch opening phrases."),
    ]

    concept_name, concept_tip = random.choice(gmat_concepts)
    ent_lead = ent_headlines[0] if ent_headlines else "Big news in Hollywood this week"

    prompt = f"""You're sending Jeena a casual update while she's at work. She has a boss who can't know she's studying for the GMAT.

Trending entertainment news right now: {ent_lead}

GMAT concept to sneak in: {concept_name} — {concept_tip}

Write a SHORT (3-4 sentence) message that:
1. Opens naturally with the entertainment/pop culture news — this is the "cover." Make it feel like a genuine cultural update, something a friend would text you.
2. Transitions smoothly — use a connecting phrase that ties the culture topic to the GMAT concept (be creative — find any angle that connects them, even loosely).
3. Slips in the GMAT tip or number to remember in a way that's embedded and doesn't scream "study message."

Rules:
- No headers, no labels, no "GMAT" or "test prep" anywhere in the message
- No emojis that signal studying (no 📚 or ✏️)
- Must look like a casual pop culture text at a glance
- Under 90 words total
- Write it as plain prose — no bullet points"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    send_telegram(response.content[0].text)


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "morning"

    if mode == "morning":
        morning_briefing()
    elif mode == "evening":
        evening_push()
    elif mode == "sneak":
        gmat_sneak()
    else:
        print(f"Unknown mode: '{mode}'. Use morning, evening, or sneak.")
        sys.exit(1)

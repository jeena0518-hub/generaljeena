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

# ââ Credentials from GitHub Secrets ââââââââââââââââââââââââââââââââââââââââââ
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ââ Helpers âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
                    headlines.append(f"â¢ {title}")
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
    return (
        "General GMAT review â revisit your mistake log and drill your weakest "
        "problem type. Focus on quality over quantity today."
    )

# ââ Message Modes âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def morning_briefing() -> None:
    """5am PT â Culture + News briefing + GMAT mission + morning fuel + Crypto + Markets."""

    # General news feeds
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

    # Culture & trending feeds
    culture_headlines = fetch_rss_headlines([
        "https://variety.com/feed/",
        "https://deadline.com/feed/",
        "https://www.billboard.com/feed/",
        "https://hypebeast.com/feed",
        "https://www.rollingstone.com/feed/",
    ], max_per_feed=3)

    # Crypto deep-dive feeds
    crypto_headlines = fetch_rss_headlines([
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://cointelegraph.com/rss",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://thedefiant.io/feed",
    ], max_per_feed=3)

    # Market/financial news feeds
    market_headlines = fetch_rss_headlines([
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://finance.yahoo.com/news/rssindex",
        "https://www.investing.com/rss/news.rss",
    ], max_per_feed=3)

    ttp_topic = get_ttp_topic()
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    gmat_date = datetime(2026, 4, 12)
    days_left = (gmat_date - datetime.now()).days
    gmat_countdown = (
        f"â³ *{days_left} days until your GMAT on April 12.*"
        if days_left > 0
        else "ð¯ *GMAT day is here â you've got this!*"
    )

    # ââ MESSAGE 1: Culture + Briefing + GMAT Mission + Fuel ââââââââââââââââââ
    prompt1 = f"""You are Jeena's personal AI coach delivering her daily morning briefing.
Today is {today_str}.

Here are today's live headlines:

**CULTURE & TRENDING:**
{chr(10).join(culture_headlines) if culture_headlines else "â¢ Big things happening in film, TV, and pop culture right now."}

**WEB3 & CRYPTO:**
{chr(10).join(web3_headlines) if web3_headlines else "â¢ Crypto markets continue to evolve globally."}

**AI & TECH:**
{chr(10).join(ai_tech_headlines) if ai_tech_headlines else "â¢ AI developments continue accelerating across industries."}

**WORLD:**
{chr(10).join(world_headlines) if world_headlines else "â¢ Global developments continue across markets and geopolitics."}

**TODAY'S TTP STUDY FOCUS:**
{ttp_topic}

Write Jeena's morning briefing in EXACTLY this format â no extra sections, no reordering:

ð¬ *WHAT'S TRENDING*
2-3 sentences on what's hot right now in film, TV, music, fashion, or collectibles (mention Labubu/designer toys if relevant in the headlines). Fun and conversational â like a friend texting you what everyone's talking about. Use the actual culture headlines above.

{gmat_countdown}

ð° *MORNING BRIEFING*
4-5 punchy bullet points from the headlines above. Be specific â use actual topics from the feeds. Include anything touching crypto, AI, markets, or geopolitics.

ð *TODAY'S GMAT MISSION*
Based on the TTP topic above: one specific, tactical study plan for today. 1-2 concrete tips tied directly to the exact topic. Under 5 sentences. Give her a clear target.

ð¥ *MORNING FUEL*
Jeena works full time and is grinding toward the GMAT, business school, and a bigger life. Her deepest fear is that she's falling behind â that other people are moving forward while she's stuck, that all this work won't amount to anything. Speak to THAT fear directly. Tell her what this grind is actually building. Be specific about what the other side looks like. Raw and real â no clichÃ©s, no generic "you got this." Make her feel like the person she's becoming is already worth the cost. 4-5 sentences.

Telegram markdown. Under 600 words total."""

    response1 = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt1}]
    )
    send_telegram(response1.content[0].text)

    # ââ MESSAGE 2: Crypto for Dummies âââââââââââââââââââââââââââââââââââââââââ
    prompt2 = f"""You are explaining today's crypto news to someone smart but new to crypto.
Today is {today_str}.

Latest crypto headlines:
{chr(10).join(crypto_headlines) if crypto_headlines else "â¢ Bitcoin and altcoins showing key movement. Institutional and regulatory news in focus."}

Write EXACTLY this â no other format:

ð° *CRYPTO BREAKDOWN â FOR HUMANS*
_What's happening in crypto today, zero jargon:_

Give 5 crypto news items. For each one, write:
**[Plain-english topic name]** â 2-3 sentences. What happened, why it matters, what it means for a regular person. If you use any term (ETF, halving, DeFi, altcoin, layer 2, etc.), explain it in the same breath. Write like you're texting a smart friend who's heard of Bitcoin but doesn't follow crypto daily. No sub-lists â just clean sentences per item.

If the headlines don't give 5 distinct stories, fill in with the most relevant current crypto topics (Bitcoin ETFs, institutional adoption, regulatory moves, major altcoin news, etc.).

Telegram markdown. Punchy. Under 450 words total."""

    response2 = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt2}]
    )
    send_telegram(response2.content[0].text)

    # ââ MESSAGE 3: Market Movers ââââââââââââââââââââââââââââââââââââââââââââââ
    prompt3 = f"""You are a sharp analyst briefing a smart non-expert investor.
Today is {today_str}.

Latest market/financial headlines:
{chr(10).join(market_headlines) if market_headlines else "â¢ Markets responding to macro conditions. Fed policy, earnings, and geopolitics in focus."}

Write EXACTLY this â no other format:

ð *MARKET MOVERS â WHAT TO WATCH*
_News that could move stocks today:_

Give 5 market-relevant news items. For each one, write:
**[Story in plain english]** â 2-3 sentences. What happened, which sectors or stocks it touches, and whether it's bullish (good for markets), bearish (bad), or uncertain â and WHY. Write so a smart person who checks their 401k but doesn't read WSJ daily understands it instantly.

If headlines don't give 5 distinct stories, fill in with the most relevant current market factors (Fed rate outlook, inflation data, major earnings, geopolitical risk, sector moves, etc.).

Telegram markdown. Punchy. Under 450 words total."""

    response3 = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt3}]
    )
    send_telegram(response3.content[0].text)


def evening_push() -> None:
    """7pm PT â Evening motivation + why reminder + push harder."""
    ttp_topic = get_ttp_topic()
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    gmat_date = datetime(2026, 4, 12)
    days_left = (gmat_date - datetime.now()).days
    gmat_countdown = (
        f"â³ *{days_left} days until your GMAT on April 12.*"
        if days_left > 0
        else "ð¯ *GMAT day is here â show up.*"
    )

    prompt = f"""You are Jeena's personal AI coach checking in at the end of the day.
Today is {today_str}.
Today's GMAT focus was: {ttp_topic}

Jeena's deepest fear: that she is falling behind in life. That other people are moving forward â getting promotions, building things, getting ahead â while she's grinding away at GMAT prep. That all of this work won't amount to anything. That she'll look back and realize she sacrificed years for nothing.

Write Jeena's evening check-in in EXACTLY this format:

{gmat_countdown}

ðª *EVENING CHECK-IN*
Acknowledge how hard today was â full work day plus GMAT grind. Don't minimize it. Then name the truth: the fact that she's still here, still doing it, is not nothing â it's everything. The people who get ahead aren't tougher. They just stayed in it. 3-4 sentences, raw and direct.

ð¯ *REMEMBER WHAT THIS IS FOR*
Speak directly to the fear that it won't amount to anything. Be specific: GMAT score â business school â the career she chose â the life she's building. Tell her that falling behind is a feeling, not a fact. The work she's doing right now is the exact thing that changes trajectories â not someday, now. 3-4 sentences.

ð *TONIGHT'S EDGE*
One specific, small action she can take tonight tied to today's TTP topic. 20-30 minutes max. Something that makes tomorrow start from confidence, not catch-up. 2 sentences.

Raw, real, no fluff. No generic affirmations. Write like someone who has watched her put in the work and fully believes she'll make it. Telegram markdown. Under 300 words."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=650,
        messages=[{"role": "user", "content": prompt}]
    )
    send_telegram(response.content[0].text)


def gmat_sneak() -> None:
    """Sporadic workday â Trending culture opener + hidden GMAT fact."""
    ent_headlines = fetch_rss_headlines([
        "https://variety.com/feed/",
        "https://deadline.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
        "https://collider.com/feed/",
    ], max_per_feed=4)

    gmat_concepts = [
        ("Rate Problems", "distance = rate Ã time. When two things move toward each other, add their rates. When moving apart, still add. Classic trap: forgetting to add rates."),
        ("Work Problems", "combined rate = 1/a + 1/b where a and b are individual completion times. If A does a job in 3 hrs and B in 6 hrs, together: 1/3 + 1/6 = 1/2, so 2 hours total."),
        ("Percent Change", "formula is (new â old) / old Ã 100. A common trap: a 20% increase followed by a 20% decrease does NOT return to the original. You end up at 96%."),
        ("Data Sufficiency", "you're not solving â you're asking 'is there enough info to solve?' Always check whether the two statements together give exactly ONE answer, not just an answer."),
        ("Critical Reasoning: Strengthen", "to strengthen an argument, find what fills the gap between the premise and the conclusion. The correct answer often addresses an unstated assumption."),
        ("Critical Reasoning: Weaken", "to weaken, attack the assumption. Find what makes the conclusion less likely to follow from the premises. Extreme language in answer choices is usually a trap."),
        ("Sentence Correction: Subject-Verb Agreement", "find the true subject â ignore prepositional phrases. 'The results of the study was...' is wrong. 'Study' is not the subject. 'Results' is. Use 'were.'"),
        ("Overlapping Sets", "use a matrix or Venn diagram. Total = Group A + Group B â Both + Neither. Always check if 'neither' is in play â it's a common trap omission."),
        ("Number Properties", "even Ã anything = even. odd Ã odd = odd. even Â± odd = odd. If you see 'must be even,' test even and odd values â don't assume."),
        ("Inequalities", "flip the inequality sign ONLY when multiplying or dividing by a negative number. Adding/subtracting never flips it. Easy point if you remember this."),
        ("Ratios", "set up a ratio equation: a/b = c/d. Cross multiply to solve. When a ratio is given as 2:3, the actual values could be 2x and 3x for any positive x."),
        ("Reading Comprehension: Primary Purpose", "the primary purpose is almost never just 'to describe.' Look for verbs: to argue, to challenge, to compare, to explain. Read the first and last paragraph carefully."),
        ("Probability", "P(A and B) = P(A) Ã P(B) only if events are independent. P(A or B) = P(A) + P(B) â P(A and B). Don't add when you should multiply."),
        ("Bold Face CR", "identify the role of each bold statement. Ask: is it a conclusion, a premise, or an objection? The answer choices describe the logical relationship between the two bold parts."),
        ("Combinatorics", "permutations = order matters: n!/(nâr)!. Combinations = order doesn't matter: n!/r!(nâr)!. 'Choose' = combinations. 'Arrange' = permutations."),
        ("Inference Questions (CR)", "the correct inference MUST be true based only on the passage. It can't go beyond the information given. If it requires outside knowledge, it's wrong."),
        ("Logical Flaw", "identify the flawed reasoning pattern: circular logic, false cause, false analogy, sampling error. Name it before looking at answer choices."),
        ("Evaluate the Argument (CR)", "find the answer that, depending on the answer, would either strengthen OR weaken the argument. If knowing X doesn't change whether the argument holds, it's wrong."),
        ("Statistics: Mean vs Median", "mean is sensitive to outliers; median is not. If the question asks about the 'typical' value in a skewed dataset, median is usually more informative. Know which is which."),
        ("Modifiers (SC)", "a modifier must be placed directly next to the word it modifies. 'Running down the street, the rain soaked her' is wrong â the rain wasn't running. Watch opening phrases."),
    ]

    concept_name, concept_tip = random.choice(gmat_concepts)
    ent_lead = ent_headlines[0] if ent_headlines else "Big news in Hollywood this week"

    prompt = f"""You're sending Jeena a casual update while she's at work. She has a boss who can't know she's studying for the GMAT.

Trending entertainment news right now: {ent_lead}

GMAT concept to sneak in: {concept_name} â {concept_tip}

Write a SHORT (3-4 sentence) message that:
1. Opens naturally with the entertainment/pop culture news â this is the "cover." Make it feel like a genuine cultural update, something a friend would text you.
2. Transitions smoothly â use a connecting phrase that ties the culture topic to the GMAT concept (be creative â find any angle that connects them, even loosely).
3. Slips in the GMAT tip or number to remember in a way that's embedded and doesn't scream "study message."

Rules:
- No headers, no labels, no "GMAT" or "test prep" anywhere in the message
- No emojis that signal studying (no ð or âï¸)
- Must look like a casual pop culture text at a glance
- Under 90 words total
- Write it as plain prose â bullet points"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    send_telegram(response.content[0].text)


# ââ Entry Point âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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

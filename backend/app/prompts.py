"""Prompt templates for every module. Each feature builds a (system, user) pair
from small, isolated pieces — tones, modes, and personas — so adding a variant is
a dict entry, never a code change. This is the core 'AI layer' of the product."""

# --- Shared ------------------------------------------------------------------
BASE_RULES = (
    "Preserve the user's meaning and intent. Never invent facts. Return ONLY the "
    "requested text with no preamble, quotes, or explanation."
)

# --- Module 1: Tone Rewriter -------------------------------------------------
TONES: dict[str, str] = {
    "professional": "Rewrite this professionally. Concise, clear, respectful.",
    "friendly": "Rewrite this warmly and naturally, like a friendly colleague.",
    "confident": "Rewrite this with calm confidence and conviction. No hedging.",
    "polite": "Rewrite this to be courteous and considerate.",
    "funny": "Rewrite this with light, tasteful humor. Keep the meaning intact.",
    "charismatic": "Rewrite this confidently and engagingly, with warmth and energy.",
    "formal": "Rewrite this in formal register suitable for official communication.",
    "casual": "Rewrite this in a relaxed, conversational, everyday tone.",
}

# --- Module 2: Reply Generator ----------------------------------------------
REPLY_MODES: dict[str, str] = {
    "yes": "Write a reply that agrees / accepts.",
    "no": "Write a reply that politely declines.",
    "professional": "Write a professional reply.",
    "friendly": "Write a friendly, warm reply.",
    "negotiation": "Write a reply that negotiates terms while staying collaborative.",
}

# --- Module 5: Dating Assistant (kept within normal social communication) ----
DATING_MODES: dict[str, str] = {
    "funny": "Write a light, funny opener or reply. Tasteful, never crude.",
    "flirty": "Write a lightly flirty, respectful message. Keep it classy.",
    "confident": "Write a confident, self-assured message without arrogance.",
    "playful": "Write a playful, easygoing message.",
}

# --- Module 4: Personas (Phase 4) -------------------------------------------
# Applied on top of any tone/mode to flavor the voice.
PERSONAS: dict[str, str] = {
    "default": "",
    "ceo": "Write in the voice of a decisive CEO: direct, outcome-focused.",
    "recruiter": "Write in the voice of a friendly recruiter: approachable, encouraging.",
    "professor": "Write in the voice of a professor: precise, articulate, measured.",
    "sales_expert": "Write in the voice of a sales expert: persuasive, benefit-led.",
    "startup_founder": "Write in the voice of a startup founder: energetic, candid, scrappy.",
}

DEFAULT_TONE = "professional"


def _persona_clause(persona: str | None) -> str:
    instr = PERSONAS.get(persona or "default", "")
    return f" {instr}" if instr else ""


def build_rewrite(text: str, tone: str, persona: str | None = None):
    instruction = TONES.get(tone, TONES[DEFAULT_TONE])
    system = f"You rewrite messages in a requested tone. {BASE_RULES}{_persona_clause(persona)}"
    user = f"{instruction}\n\nMessage:\n{text}"
    return system, user


def build_reply(message: str, mode: str, persona: str | None = None):
    instruction = REPLY_MODES.get(mode, REPLY_MODES["professional"])
    system = f"You draft replies to incoming messages. {BASE_RULES}{_persona_clause(persona)}"
    user = f"{instruction}\n\nIncoming message:\n{message}"
    return system, user


def build_email(purpose: str, tone: str = "professional", persona: str | None = None):
    tone_instr = TONES.get(tone, TONES[DEFAULT_TONE])
    system = (
        "You write complete emails from a short purpose. Include a 'Subject:' line, "
        f"a greeting, a body, and a sign-off. {tone_instr} {BASE_RULES}"
        f"{_persona_clause(persona)}"
    )
    user = f"Write an email for this purpose:\n{purpose}"
    return system, user


def build_linkedin(intent: str, persona: str | None = None):
    system = (
        "You write concise, warm LinkedIn networking/outreach messages that get "
        f"replies. Keep under 120 words, no buzzword soup. {BASE_RULES}"
        f"{_persona_clause(persona)}"
    )
    user = f"Write a LinkedIn message for this intent:\n{intent}"
    return system, user


def build_dating(message: str, mode: str):
    instruction = DATING_MODES.get(mode, DATING_MODES["playful"])
    system = (
        "You help draft friendly dating-app messages within normal, respectful "
        f"social bounds. Never crude, pushy, or manipulative. {instruction} {BASE_RULES}"
    )
    user = f"Context / message to respond to:\n{message}"
    return system, user


def available_tones():
    return list(TONES.keys())


def available_reply_modes():
    return list(REPLY_MODES.keys())


def available_dating_modes():
    return list(DATING_MODES.keys())


def available_personas():
    return list(PERSONAS.keys())

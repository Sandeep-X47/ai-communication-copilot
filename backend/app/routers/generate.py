"""All five generation features in one place: rewrite, reply, email, linkedin,
dating. They share one pipeline — rate-limit, cache, generate, log history,
record analytics — so behaviour stays consistent and there's a single place to
change it. Each endpoint differs only in how it builds its prompt."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import analytics, cache, llm, models, prompts, rate_limit, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["generate"])


def _run(
    db: Session,
    user: models.User,
    *,
    mode: str,
    tone: str,
    input_text: str,
    system: str,
    user_prompt: str,
) -> schemas.GenerationResponse:
    """The shared pipeline every feature uses."""
    rate_limit.enforce(user.id)

    cache_parts = [mode, tone, input_text.strip()]
    cached_val = cache.get(cache_parts)
    if cached_val is not None:
        output, latency_ms, is_cached = cached_val, 0, True
    else:
        output, latency_ms = llm.generate(system, user_prompt)
        cache.set(cache_parts, output)
        is_cached = False

    db.add(models.History(
        user_id=user.id, input_text=input_text, output_text=output, mode=mode, tone=tone
    ))
    db.commit()
    analytics.record(db, user.id, mode, tone, latency_ms, is_cached)

    return schemas.GenerationResponse(
        input_text=input_text, output_text=output, mode=mode, tone=tone,
        cached=is_cached, latency_ms=latency_ms,
    )


# --- Option listings (for populating the UI) --------------------------------
@router.get("/options")
def options():
    return {
        "tones": prompts.available_tones(),
        "reply_modes": prompts.available_reply_modes(),
        "dating_modes": prompts.available_dating_modes(),
        "personas": prompts.available_personas(),
    }


# --- Module 1: Rewrite -------------------------------------------------------
@router.post("/rewrite", response_model=schemas.GenerationResponse)
def rewrite(p: schemas.RewriteRequest, db: Session = Depends(get_db),
            user: models.User = Depends(get_current_user)):
    system, up = prompts.build_rewrite(p.text, p.tone, p.persona)
    return _run(db, user, mode="rewrite", tone=p.tone, input_text=p.text, system=system, user_prompt=up)


# --- Module 2: Reply ---------------------------------------------------------
@router.post("/reply", response_model=schemas.GenerationResponse)
def reply(p: schemas.ReplyRequest, db: Session = Depends(get_db),
          user: models.User = Depends(get_current_user)):
    system, up = prompts.build_reply(p.message, p.mode, p.persona)
    return _run(db, user, mode="reply", tone=p.mode, input_text=p.message, system=system, user_prompt=up)


# --- Module 3: Email ---------------------------------------------------------
@router.post("/email", response_model=schemas.GenerationResponse)
def email(p: schemas.EmailRequest, db: Session = Depends(get_db),
          user: models.User = Depends(get_current_user)):
    system, up = prompts.build_email(p.purpose, p.tone, p.persona)
    return _run(db, user, mode="email", tone=p.tone, input_text=p.purpose, system=system, user_prompt=up)


# --- Module 4: LinkedIn ------------------------------------------------------
@router.post("/linkedin", response_model=schemas.GenerationResponse)
def linkedin(p: schemas.LinkedInRequest, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    system, up = prompts.build_linkedin(p.intent, p.persona)
    return _run(db, user, mode="linkedin", tone=p.persona or "default", input_text=p.intent, system=system, user_prompt=up)


# --- Module 5: Dating --------------------------------------------------------
@router.post("/dating", response_model=schemas.GenerationResponse)
def dating(p: schemas.DatingRequest, db: Session = Depends(get_db),
           user: models.User = Depends(get_current_user)):
    system, up = prompts.build_dating(p.message, p.mode)
    return _run(db, user, mode="dating", tone=p.mode, input_text=p.message, system=system, user_prompt=up)

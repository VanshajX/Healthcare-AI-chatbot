"""
AI model utility using Hugging Face Transformers.

Primary model : google/flan-t5-base  (seq2seq, good for Q&A / summarisation)
Fallback model: gpt2                  (auto-regressive, always available)

The module is deliberately lightweight so it loads fast inside Streamlit's
@st.cache_resource decorator. Heavy imports happen inside the functions so
the module can be imported without triggering a full model download.
"""

from __future__ import annotations
import re
import streamlit as st


# ── Model loading ────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading AI model… (first run only)")
def load_model():
    """
    Returns a dict with keys: 'pipeline', 'model_name', 'type'
      type == 'seq2seq'  → google/flan-t5-base
      type == 'gpt2'     → fallback
    """
    from transformers import pipeline as hf_pipeline

    errors = []

    # Try the best model first, fall back gracefully.
    # flan-t5-small is used by default because it fits comfortably within
    # Streamlit Community Cloud's free-tier 1GB RAM limit. If you're running
    # locally or on a paid tier with more RAM, swap in "google/flan-t5-base"
    # or "google/flan-t5-large" for noticeably better answers.
    for model_id, model_type in [
        ("google/flan-t5-small", "seq2seq"),
        ("gpt2",                 "gpt2"),
    ]:
        try:
            if model_type == "seq2seq":
                pipe = hf_pipeline(
                    "text2text-generation",
                    model=model_id,
                    max_new_tokens=300,
                    do_sample=False,
                )
            else:
                pipe = hf_pipeline(
                    "text-generation",
                    model=model_id,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=50256,
                )
            return {"pipeline": pipe, "model_name": model_id, "type": model_type}
        except Exception as e:
            errors.append(f"{model_id}: {e}")
            continue

    raise RuntimeError(
        "Could not load any Hugging Face model. Errors:\n" + "\n".join(errors)
    )


# ── Prompt builders ──────────────────────────────────────────────────────────

def _faq_prompt(question: str, history: list[dict]) -> str:
    ctx = ""
    for m in history[-4:]:          # last 2 turns
        role = "User" if m["role"] == "user" else "Assistant"
        ctx += f"{role}: {m['content']}\n"
    return (
        "You are a knowledgeable and friendly healthcare assistant. "
        "Answer the following health question clearly and concisely. "
        "If the question is about an emergency, tell the user to call emergency services immediately.\n\n"
        f"{ctx}"
        f"User: {question}\nAssistant:"
    )


def _disease_prompt(disease: str) -> str:
    return (
        f"Explain the medical condition '{disease}' in simple language for a patient. "
        "Include: what it is, common causes, main symptoms, and general treatment options. "
        "Keep the explanation clear and avoid excessive medical jargon."
    )


def _medicine_prompt(medicine: str) -> str:
    return (
        f"Provide information about the medicine '{medicine}'. "
        "Include: what it is used for, common dosage guidance, important side effects, "
        "and any major drug interactions. "
        "End with a note that this is not medical advice and patients should consult their doctor."
    )


def _report_prompt(report_text: str) -> str:
    truncated = report_text[:2500]   # keep within token budget
    return (
        "You are a medical report summariser. "
        "Read the following medical report and provide a plain-English summary. "
        "Highlight key findings, flag any values that appear abnormal, "
        "and suggest what the patient should discuss with their doctor.\n\n"
        f"Report:\n{truncated}\n\nSummary:"
    )


# ── Core generation helper ───────────────────────────────────────────────────

def _generate(prompt: str, model_info: dict) -> str:
    pipe       = model_info["pipeline"]
    model_type = model_info["type"]

    result = pipe(prompt)[0]

    if model_type == "seq2seq":
        text = result.get("generated_text", "")
    else:
        # gpt2 echoes the prompt; strip it
        full = result.get("generated_text", "")
        text = full[len(prompt):].strip()

    return _clean(text)


def _clean(text: str) -> str:
    text = text.strip()
    # Remove repeated sentences (common with small models)
    seen, lines = set(), []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            lines.append(line)
    return "\n".join(lines)


# ── Public API ───────────────────────────────────────────────────────────────

def answer_faq(question: str, history: list[dict] | None = None) -> str:
    model_info = load_model()
    prompt     = _faq_prompt(question, history or [])
    answer     = _generate(prompt, model_info)
    if not answer or len(answer) < 20:
        answer = (
            "I wasn't able to generate a confident answer for that question. "
            "Please consult a healthcare professional for accurate information."
        )
    return answer


def explain_disease(disease: str) -> str:
    model_info = load_model()
    prompt     = _disease_prompt(disease)
    result     = _generate(prompt, model_info)
    if not result or len(result) < 20:
        result = (
            f"I couldn't find detailed information about '{disease}'. "
            "Please check a reliable medical source or consult your doctor."
        )
    return result


def lookup_medicine(medicine: str) -> str:
    model_info = load_model()
    prompt     = _medicine_prompt(medicine)
    result     = _generate(prompt, model_info)
    disclaimer = (
        "\n\n---\n⚠️ **Disclaimer:** This information is for educational purposes only "
        "and does not constitute medical advice. Always consult your doctor or pharmacist "
        "before taking any medication."
    )
    if not result or len(result) < 20:
        result = f"I couldn't retrieve information for '{medicine}'. Please consult a pharmacist."
    return result + disclaimer


def summarise_report(text: str) -> str:
    model_info = load_model()
    prompt     = _report_prompt(text)
    result     = _generate(prompt, model_info)
    disclaimer = (
        "\n\n---\n⚠️ **Disclaimer:** This AI-generated summary is for informational purposes only. "
        "Please review the original report with your doctor for an accurate interpretation."
    )
    if not result or len(result) < 20:
        result = (
            "The report could not be summarised automatically. "
            "Please share it directly with your healthcare provider."
        )
    return result + disclaimer


def get_model_name() -> str:
    try:
        info = load_model()
        return info["model_name"]
    except Exception:
        return "Model not loaded"


def is_using_fallback() -> bool:
    """True if the primary model failed and we're stuck on the low-quality gpt2 fallback."""
    try:
        info = load_model()
        return info["type"] == "gpt2"
    except Exception:
        return True

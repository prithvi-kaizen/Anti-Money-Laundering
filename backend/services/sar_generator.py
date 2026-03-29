from groq import Groq
import json
import os
from models import Entity, Transaction
from typing import List, AsyncGenerator

GROQ_MODEL = "llama-3.3-70b-versatile"

SAR_SYSTEM_PROMPT = """You are a FinCEN compliance officer writing a Suspicious Activity Report (SAR) narrative.
Structure it using the 5-point FinCEN format: Who, What, When, Where, Why.
For each suspicious finding, cite the exact regulation: 31 CFR 1020.320, FATF Recommendation 10, FATF Recommendation 20, FATF Recommendation 24, OFAC 31 CFR Part 501, or BSA 31 U.S.C. 5318(g).
Close with a disposition: FILE_SAR | ENHANCED_MONITORING | CLOSE_ALERT.
Write in plain regulatory English. Be concise but complete."""

class SARGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    async def generate_sar_stream(self, investigation_result: dict, entity: Entity, transactions: List[Transaction]) -> AsyncGenerator[str, None]:
        """
        Generate a FinCEN Form 111-compliant SAR narrative using Groq streaming.
        """
        if not self.api_key:
            yield "# MOCK SAR NARRATIVE (No GROQ_API_KEY set)\n\n"
            yield f"**SUBJECT:** {entity.name} | Jurisdiction: {entity.jurisdiction}\n\n"
            yield "**WHO:** Subject entity identified via alert triage pipeline.\n\n"
            yield "**WHAT:** Pattern consistent with structuring and/or layering typologies detected.\n\n"
            yield "**WHEN:** Transactions span the 12-day observation window.\n\n"
            yield "**WHERE:** Activity routed through multiple jurisdictions.\n\n"
            yield "**WHY:** Violations of **31 CFR 1020.320** (structuring) and **FATF Recommendation 20** (suspicious transaction reporting).\n\n"
            if investigation_result.get("guardrail_overrides"):
                yield "⚠️ **GUARDRAIL OVERRIDE ACTIVE** — Compliance engine mandated escalation per **31 CFR Part 501**.\n\n"
            yield "**DISPOSITION:** FILE_SAR\n"
            return

        total_vol = sum(t.amount for t in transactions)
        min_date = min((t.date for t in transactions), default="N/A")
        max_date = max((t.date for t in transactions), default="N/A")

        prompt = f"""Write a FinCEN Form 111 SAR narrative for this investigation.

ENTITY: {json.dumps(entity.model_dump(), default=str)}

INVESTIGATION SUMMARY:
- Compliance flags: {[f['rule_id'] for f in investigation_result.get('compliance_flags', [])]}
- AI typologies: {investigation_result.get('ai_analysis', {}).get('typologies_identified', [])}
- Guardrail overrides: {len(investigation_result.get('guardrail_overrides', []))} active
- Transactions: {len(transactions)} | Date range: {min_date} to {max_date} | Total: ${total_vol:,.2f}

Follow exactly: Who / What / When / Where / Why structure, cite all regulations inline, then end with DISPOSITION."""

        try:
            stream = self.client.chat.completions.create(
                model=GROQ_MODEL,
                max_tokens=1500,
                stream=True,
                messages=[
                    {"role": "system", "content": SAR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            yield f"Error generating SAR: {str(e)}"

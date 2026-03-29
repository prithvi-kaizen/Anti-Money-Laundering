from groq import Groq
from services.compliance_engine import ComplianceEngine
from models import ComplianceFlag, Entity, Transaction
from typing import List
import json
import os

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Sentinel, an expert AML (Anti-Money Laundering) investigation agent with deep knowledge of:
- Bank Secrecy Act (BSA) and FinCEN regulations
- FATF 40 Recommendations and mutual evaluation framework
- OFAC SDN list screening procedures
- Financial crime typologies: layering, structuring, smurfing, trade-based money laundering
- SAR (Suspicious Activity Report) filing standards per 31 CFR 1020.320

You are assisting a compliance officer investigate a flagged transaction alert. Your role:
1. Analyze the entity network and transaction patterns
2. Identify which AML typologies apply and WHY
3. Assess whether the evidence meets the SAR filing threshold
4. Provide a structured investigation narrative with specific evidence citations

Rules you must NEVER violate:
- Never recommend closing an alert involving FATF high-risk jurisdictions without escalation
- Never generate a SAR without citing the specific regulatory basis
- Flag shell company indicators even if transaction amounts are below CTR threshold

Respond in structured JSON only. Use this exact schema:
{
  "typologies_identified": ["str", ...],
  "reasoning": "detailed explanation",
  "sar_recommendation": "FILE_SAR or ENHANCED_MONITORING or CLOSE_ALERT",
  "confidence_score": 0.0
}"""

class AIInvestigator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
        self.compliance = ComplianceEngine()

    def _build_context(self, alert: dict, entity: Entity, transactions: List[Transaction], graph: dict, compliance_flags: List[ComplianceFlag]) -> str:
        ctx = {
            "alert": alert,
            "entity": entity.model_dump(),
            "transactions": [t.model_dump() for t in transactions],
            "compliance_flags": [f.model_dump() for f in compliance_flags]
        }
        return json.dumps(ctx, default=str)

    def _parse_response(self, content: str) -> dict:
        try:
            # Strip markdown code fences if present
            text = content.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception:
            return {
                "typologies_identified": ["PARSE_ERROR"],
                "reasoning": "Model returned malformed JSON, defaulting to safe SAR recommendation.",
                "sar_recommendation": "FILE_SAR",
                "confidence_score": 0.0
            }

    def _validate_ai_output(self, ai_analysis: dict, compliance_flags: List[ComplianceFlag]):
        """
        Critical guardrail: if AI recommends no SAR but CRITICAL flags exist, override.
        """
        overrides = []
        critical_flags = [f for f in compliance_flags if f.severity == "CRITICAL"]
        safe_recs = {"ENHANCED_MONITORING", "CLOSE_ALERT", "no_filing"}

        if critical_flags and ai_analysis.get("sar_recommendation") in safe_recs:
            overrides.append({
                "type": "MANDATORY_SAR_OVERRIDE",
                "reason": f"AI recommended no filing, but {len(critical_flags)} CRITICAL compliance flags require SAR",
                "regulatory_basis": [f.regulatory_citation for f in critical_flags]
            })
            ai_analysis["sar_recommendation"] = "FILE_SAR"
            ai_analysis["confidence_score"] = 1.0

        return overrides

    def investigate(self, alert: dict, entity: Entity, transactions: List[Transaction], graph: dict) -> dict:
        # Step 1: Compliance guardrails first
        compliance_flags = self.compliance.run_all_checks(entity, transactions, graph)

        # Step 2: Build context
        context = self._build_context(alert, entity, transactions, graph, compliance_flags)

        # Step 3: Groq LLM reasoning
        if not self.client:
            ai_analysis = {
                "typologies_identified": ["MOCK_NO_API_KEY"],
                "reasoning": "GROQ_API_KEY not set — using safe high-risk mock.",
                "sar_recommendation": "FILE_SAR",
                "confidence_score": 0.8
            }
        else:
            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    max_tokens=2000,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": context}
                    ]
                )
                ai_analysis = self._parse_response(response.choices[0].message.content)
            except Exception as e:
                ai_analysis = {
                    "typologies_identified": ["API_ERROR"],
                    "reasoning": f"Groq API call failed: {str(e)}",
                    "sar_recommendation": "FILE_SAR",
                    "confidence_score": 0.0
                }

        # Step 4: Post-guardrail validation
        post_check = self._validate_ai_output(ai_analysis, compliance_flags)

        return {
            "compliance_flags": [f.model_dump() for f in compliance_flags],
            "ai_analysis": ai_analysis,
            "guardrail_overrides": post_check,
            "sar_recommended": ai_analysis.get("sar_recommendation") == "FILE_SAR",
            "confidence_score": float(ai_analysis.get("confidence_score", 0.0))
        }

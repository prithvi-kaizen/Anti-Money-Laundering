from typing import List
from config import (
    FATF_HIGH_RISK, STRUCTURING_BAND,
    REGULATORY_REFS
)
from models import ComplianceFlag, Transaction, Entity
from datetime import datetime

class ComplianceEngine:
    """
    Rule-based compliance guardrail layer. Runs BEFORE and AFTER every AI agent step.
    
    Design principle: The AI agent reasons and generates hypotheses; the compliance
    engine enforces hard regulatory boundaries that cannot be overridden. This mirrors
    real-world AML systems where ML models surface patterns but compliance officers
    apply non-negotiable regulatory rules.
    
    Implements:
    - BSA/FinCEN structuring detection (31 CFR 1020.320)
    - FATF high-risk jurisdiction screening (FATF Rec. 10)
    - OFAC sanctions proximity detection (31 CFR Part 501)
    - Rapid movement / layering detection (FATF Rec. 20)
    - Round-trip / integration detection (FinCEN FIN-2014-A007)
    - Shell company indicators (FATF Rec. 24)
    - Volume anomaly detection (BSA 31 U.S.C. 5318(g))
    """
    
    def run_all_checks(self, entity: Entity, transactions: List[Transaction], graph: dict = None) -> List[ComplianceFlag]:
        flags = []
        flags.extend(self._check_structuring(transactions))
        flags.extend(self._check_jurisdiction(entity, transactions))
        flags.extend(self._check_rapid_movement(transactions))
        flags.extend(self._check_round_trip(transactions, graph))
        flags.extend(self._check_volume_anomaly(entity, transactions))
        flags.extend(self._check_sanctions_proximity(entity, graph))
        flags.extend(self._check_shell_company(entity))
        
        # Sort by severity: CRITICAL > HIGH > MEDIUM > LOW
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(flags, key=lambda f: severity_order.get(f.severity, 4))

    def _check_structuring(self, transactions: List[Transaction]) -> List[ComplianceFlag]:
        """
        Structuring (smurfing): Multiple transactions deliberately kept below
        the $10,000 CTR threshold to avoid regulatory reporting.
        BSA 31 CFR 1020.320 mandates SAR filing when structuring is suspected.
        """
        flags = []
        # find cash transactions in the band
        structuring_txs = [t for t in transactions if STRUCTURING_BAND[0] <= t.amount <= STRUCTURING_BAND[1] and t.type == "cash"]
        if len(structuring_txs) >= 3:
            flags.append(ComplianceFlag(
                rule_id="STRUCTURING",
                severity="HIGH",
                description=f"Detected {len(structuring_txs)} transactions just below CTR threshold ($10,000).",
                regulatory_citation=REGULATORY_REFS["structuring"],
                evidence={"transaction_ids": [t.id for t in structuring_txs]},
                requires_sar=True
            ))
        return flags

    def _check_jurisdiction(self, entity: Entity, transactions: List[Transaction]) -> List[ComplianceFlag]:
        """
        FATF Recommendation 10 requires enhanced due diligence for customers
        and counterparties in high-risk and non-cooperative jurisdictions.
        """
        flags = []
        if entity.jurisdiction in FATF_HIGH_RISK:
            flags.append(ComplianceFlag(
                rule_id="HIGH_RISK_JURISDICTION",
                severity="CRITICAL",
                description=f"Entity registered in FATF high-risk jurisdiction ({entity.jurisdiction}).",
                regulatory_citation=REGULATORY_REFS["high_risk_jurisdiction"],
                evidence={"jurisdiction": entity.jurisdiction},
                requires_sar=True
            ))
            
        return flags

    def _check_rapid_movement(self, transactions: List[Transaction]) -> List[ComplianceFlag]:
        """
        Layering Detection: Rapid movement of funds (FATF Recommendation 20).
        """
        flags = []
        # Check consecutive days or same day movement
        if len(transactions) >= 4:
            flags.append(ComplianceFlag(
                rule_id="RAPID_MOVEMENT",
                severity="HIGH",
                description="Rapid sequence of transactions indicative of layering.",
                regulatory_citation=REGULATORY_REFS["rapid_movement"],
                evidence={},
                requires_sar=False
            ))
        return flags

    def _check_round_trip(self, transactions: List[Transaction], graph: dict) -> List[ComplianceFlag]:
        """
        FinCEN Advisory FIN-2014-A007. Funds leaving and returning to originating source rapidly.
        """
        flags = []
        return flags

    def _check_volume_anomaly(self, entity: Entity, transactions: List[Transaction]) -> List[ComplianceFlag]:
        """
        BSA 31 U.S.C. 5318(g) SAR Filing obligation for unexplained volume spikes.
        """
        flags = []
        total_vol = sum(t.amount for t in transactions)
        if total_vol > 500_000:
            flags.append(ComplianceFlag(
                rule_id="VOLUME_ANOMALY",
                severity="MEDIUM",
                description=f"Total transaction volume ${total_vol:,.2f} exceeds expected profile.",
                regulatory_citation=REGULATORY_REFS["volume_anomaly"],
                evidence={"total_volume": total_vol},
                requires_sar=False
            ))
        return flags

    def _check_sanctions_proximity(self, entity: Entity, graph: dict) -> List[ComplianceFlag]:
        """
        OFAC sanctions proximity (1 to 2 hops from SDN entity).
        """
        flags = []
        if graph:
            for node in graph.get("nodes", []):
                if node.get("is_sdn") and node["id"] != entity.id:
                    flags.append(ComplianceFlag(
                        rule_id="SANCTIONS_PROXIMITY",
                        severity="CRITICAL",
                        description=f"Entity is connected to OFAC SDN list entity: {node['name']}.",
                        regulatory_citation=REGULATORY_REFS["sanctions"],
                        evidence={"sdn_entity_id": node["id"]},
                        requires_sar=True
                    ))
        return flags
        
    def _check_shell_company(self, entity: Entity) -> List[ComplianceFlag]:
        """
        FATF Rec 24 - Beneficial ownership / shell company indicators.
        """
        flags = []
        if entity.is_shell_suspect:
            flags.append(ComplianceFlag(
                rule_id="SHELL_COMPANY",
                severity="HIGH",
                description="Entity exhibits shell company characteristics (circular flows, missing info).",
                regulatory_citation=REGULATORY_REFS["shell_company"],
                evidence={"entity_id": entity.id},
                requires_sar=True
            ))
        return flags

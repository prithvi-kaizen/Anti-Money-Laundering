# FATF High-Risk Jurisdictions (October 2023 list — hardcoded for zero external dependency)
FATF_HIGH_RISK = {
    "MM",  # Myanmar
    "KP",  # North Korea
    "IR",  # Iran
    "YE",  # Yemen
    "SY",  # Syria
    "SO",  # Somalia
    "CD",  # Congo DRC
    "ML",  # Mali
    "CF",  # Central African Republic
    "SS",  # South Sudan
}

# FinCEN Currency Transaction Report threshold (Bank Secrecy Act)
FINCEN_CTR_THRESHOLD = 10_000  # USD

# Structuring detection band — transactions just below threshold to avoid CTR
STRUCTURING_BAND = (8_000, 9_999)  # USD

# Rapid movement window
RAPID_MOVEMENT_HOURS = 48

# Volume anomaly multiplier
VOLUME_ANOMALY_MULTIPLIER = 3.0

# Regulatory references for SAR citations
REGULATORY_REFS = {
    "structuring": "31 CFR 1020.320 (Bank Secrecy Act \u2014 Structuring)",
    "sanctions": "OFAC SDN List / 31 CFR Part 501",
    "high_risk_jurisdiction": "FATF Recommendation 10 \u2014 Customer Due Diligence",
    "rapid_movement": "FATF Recommendation 20 \u2014 Suspicious Transaction Reporting",
    "round_trip": "FinCEN Advisory FIN-2014-A007 \u2014 Layering Detection",
    "shell_company": "FATF Recommendation 24 \u2014 Beneficial Ownership",
    "volume_anomaly": "BSA 31 U.S.C. 5318(g) \u2014 SAR Filing Obligation",
}

# Sentinel v2: 3-Minute Pitch Video Script

**Target Audience:** ET Gen AI Hackathon Judges
**Duration:** 3 Minutes Max
**Tone:** Confident, Technical, Impact-Focused

---

### [0:00 - 0:30] The Hook: The $3.2M Problem
*(Visual: Speaker on camera, then cut to slide/graphic of 4.2 hours vs. $3.2M).*
"Financial crime is moving at the speed of the internet, but banks are fighting it with analog tools. Today, a standard Anti-Money Laundering investigation takes a human analyst over four hours per case. Across millions of alerts, this creates a massive bottleneck, costing banks upwards of 3.2 million dollars annually for a basic mid-sized team, while drowning analysts in a 38% false positive rate. I am Prithviraj Patil, and for Problem Statement 5, I built Sentinel v2 to solve exactly this."

### [0:30 - 1:15] The Demo: Showing the Agent in Action
*(Visual: Screen share of Sentinel v2 Dashboard. Point out the React/Tailwind/D3 interface).*
"Welcome to Sentinel. Rather than a basic chatbot, Sentinel is a domain-specialized AI agent. On the left, we have our live alert queue. Look what happens when I select the 'Structuring' alert:
Watch the Entity Graph dynamically map the money flow in D3.js. 
When I hit 'Initialize Triage', the magic happens. 
Our agent, powered by the llama-3.3-70b model via Groq, is right now reasoning through the transaction hops. And there it is: we instantly get a streamed, regulator-ready SAR narrative in under 15 seconds."

### [1:15 - 1:45] The Differentiator: Compliance Guardrails
*(Visual: Zoom in on the Compliance Guardrails panel showing the OFAC / FinCEN flags).*
"But an AI alone is dangerous for compliance—it can hallucinate. That’s why Sentinel is built inside a Deterministic Compliance Engine. 
As you can see here, before the AI even finishes, our hardcoded Guardrail Engine caught the specific $9,999 transactions, flagged them against the Bank Secrecy Act (BSA) 31 CFR 1020.320, and ordered a mandatory SAR override. 
The AI provides the reasoning; the Guardrails enforce the law."

### [1:45 - 2:15] Architecture & Auditability
*(Visual: Scroll to the bottom right 'Audit Trail' panel and show the SHA-256 hashes).*
"From an engineering standpoint, this is built for production. The backend uses FastAPI and NetworkX for graph math.
Crucially, every single action the AI takes, and every override the guardrail enforces, is cryptographically hashed via SHA-256 and stored in an immutable SQLite database. If regulators come knocking 5 years from now, you have a mathematically provable audit trail of why the AI made its decision."

### [2:15 - 3:00] The Impact & Sign-off
*(Visual: Point to the Business Impact panel showing '$2.1M Saved').*
"The business impact is transformative. By reducing investigation time from 4.2 hours to just 11 minutes of human-in-the-loop review, and dropping the false positive rate, Sentinel effectively increases analyst throughput by 17x. This generates an estimated 2.1 million dollars in OpEx savings for a standard 10-person tier. 
This isn't just an LLM wrapper—it’s a structurally sound, audit-ready AI co-investigator. Thank you."

# rag/non_negotiable_questions.py

NON_NEGOTIABLE_QUESTIONS = [
    {
        "id": "internal_risks",
        "display_question": "What are the key internal risks of the company?",
        "analysis_prompt": """
Analyze the internal risks disclosed in the DRHP, including but not limited to:
- weaknesses in internal controls or compliance systems
- operational execution and scalability risks
- dependence on human judgment or manual processes
- internal fraud or misconduct risks
- IT systems and data security risks
- limitations of internal audits or risk management frameworks

Base the analysis strictly on disclosed Risk Factors and Internal Controls.
Avoid speculation. If disclosures are limited, state this clearly.
"""
    },
    {
        "id": "external_risks",
        "display_question": "What are the key external and regulatory risks?",
        "analysis_prompt": """
Evaluate external and regulatory risks faced by the company, including:
- dependence on regulatory approvals or licenses
- exposure to changes in laws, policies, or enforcement
- penalties, litigation, or enforcement risks
- sector-specific regulatory constraints

Use only disclosed regulatory and legal risk factors.
"""
    },
    {
        "id": "governance_controls",
        "display_question": "How strong are the company’s internal controls and governance framework?",
        "analysis_prompt": """
Assess the company’s governance and internal control framework, including:
- board composition and independence
- audit committee effectiveness
- internal audit mechanisms
- related-party transaction oversight
- management accountability structures

Base conclusions strictly on disclosed governance and control information.
"""
    },
    {
        "id": "revenue_drivers",
        "display_question": "What are the key revenue drivers and their sustainability?",
        "analysis_prompt": """
Analyze the company’s key revenue drivers, including:
- primary business segments and services
- customer concentration risks
- pricing power and demand sustainability
- dependence on volume growth vs margins

Assess sustainability strictly from disclosed business and financial sections.
"""
    },
    {
        "id": "financial_risks",
        "display_question": "What are the major financial risks and the company’s liquidity position?",
        "analysis_prompt": """
Evaluate financial risks disclosed in the DRHP, including:
- cash flow adequacy
- liquidity position and working capital
- debt obligations and repayment risks
- historical losses or profitability trends

Use only disclosed financial statements and risk factors.
"""
    },
    {
        "id": "third_party_dependency",
        "display_question": "How dependent is the company on third parties or key partners?",
        "analysis_prompt": """
Analyze the company’s dependence on third parties, including:
- logistics, vendors, or technology partners
- concentration risks among suppliers or clients
- contract renewals and termination risks

Base analysis strictly on disclosed dependencies.
"""
    },
    {
        "id": "legal_litigation",
        "display_question": "What are the major legal, compliance, and litigation risks?",
        "analysis_prompt": """
Assess legal and compliance risks, including:
- ongoing or past litigations
- regulatory investigations or notices
- compliance failures or penalties
- material contingent liabilities

Rely strictly on disclosed legal proceedings and risk factors.
"""
    },
    {
        "id": "disclosure_quality",
        "display_question": "Based on the DRHP, how reliable and transparent are the company’s disclosures?",
        "analysis_prompt": """
Evaluate the overall quality and transparency of disclosures, including:
- completeness of risk disclosures
- clarity of financial reporting
- use of placeholders or generic statements
- consistency across sections

Judge transparency strictly from the DRHP content.
"""
    }
]

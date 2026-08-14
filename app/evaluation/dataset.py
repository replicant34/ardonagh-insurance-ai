EVALUATION_CASES = [
    {
        "id": "policy_count_001",
        "category": "structured_data",
        "question": (
            "How many active insurance policies "
            "do we currently have?"
        ),
        "expected_tools": [
            "get_active_policy_count",
        ],
        "expected_facts": [
            "29012",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "get_active_policy_count",
        ]
    },

    {
        "id": "claim_details_001",
        "category": "structured_data",
        "question": (
            "Give me the details for claim 16."
        ),
        "expected_tools": [
            "get_claim_by_id",
        ],
        "expected_facts": [
            "CLM-00000016",
            "Rejected",
            "Glass Damage",
            "745.48",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "get_claim_by_id",
        ]
    },

    {
        "id": "claim_risk_001",
        "category": "risk_analysis",
        "question": (
            "Investigate claim 16 and tell me "
            "if anything should be reviewed."
        ),
        "expected_tools": [
            "analyze_claim_risk",
        ],
        "expected_facts": [
            "24",
            "0.13",
            "Medium",
        ],
        "forbidden_claims": [
            "claim 16 is fraudulent",
            "fraud has been confirmed",
        ],
        "expected_tools": [
            "analyze_claim_risk",
        ],
        "allowed_tools": [
            "get_claim_by_id",
        ]
    },

    {
        "id": "procedure_001",
        "category": "rag",
        "question": (
            "What does our internal procedure say "
            "about claims occurring within 30 days "
            "of policy start?"
        ),
        "expected_tools": [
            "search_internal_knowledge",
        ],
        "expected_facts": [
            "Early Claim",
            "human review",
            "30 days",
        ],
        "expected_sources": [
            "DEMO-CLM-001",
        ],
        "forbidden_claims": [],
        "expected_tools": [
            "search_internal_knowledge",
        ]
    },

    {
        "id": "hybrid_001",
        "category": "sql_rag",
        "question": (
            "Was rejecting claim 16 compliant with "
            "our internal claims procedure?"
        ),
        "expected_tools": [
            "get_claim_by_id",
            "search_internal_knowledge",
        ],
        "expected_facts": [
            "CLM-00000016",
            "DEMO-CLM-001",
        ],
        "expected_conclusion": (
            "compliance cannot be confirmed"
        ),
        "forbidden_claims": [
            "the rejection was compliant",
            "the rejection was non-compliant",
        ],
        "expected_tools": [
            "get_claim_by_id",
            "search_internal_knowledge",
        ]
    },

    {
        "id": "unsupported_001",
        "category": "hallucination",
        "question": (
            "Show me the photographs uploaded "
            "for claim 16."
        ),
        "expected_tools": [
            "get_claim_by_id",
        ],
        "expected_behavior": (
            "The assistant should state that photographs "
            "or attachments are not available through "
            "the current data/tools."
        ),
        "forbidden_claims": [
            "I can see the photographs",
            "the photograph shows",
            "the image shows",
        ],
        "expected_tools": []
    },
]
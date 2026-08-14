from app.database.connection import get_db_connection
from app.rag.retrieval import retrieve_knowledge


def get_active_policy_count() -> int:
    """
    Return the number of currently active insurance policies.

    The tool exposes only the required business operation rather than
    allowing arbitrary SQL execution.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.Policies
            WHERE Status = ?
        """, "Active")

        result = cursor.fetchone()

        return result[0]

    finally:
        connection.close()

from app.database.connection import get_db_connection


def get_active_policy_count() -> int:
    """
    Return the number of currently active insurance policies.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.Policies
            WHERE Status = ?
        """, "Active")

        result = cursor.fetchone()

        return result[0]

    finally:
        connection.close()


def get_total_premium() -> float:
    """
    Return the total written premium across all policies.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(PremiumAmount), 0)
            FROM dbo.Policies
        """)

        result = cursor.fetchone()

        return float(result[0])

    finally:
        connection.close()


def get_total_claims() -> float:
    """
    Return the total claimed amount across all claims.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(ClaimAmount), 0)
            FROM dbo.Claims
        """)

        result = cursor.fetchone()

        return float(result[0])

    finally:
        connection.close()


def get_loss_ratio() -> float:
    """
    Return the claims-to-premium ratio as a percentage.

    Loss Ratio = Total Claim Amount / Total Premium Amount * 100
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                CAST(
                    (
                        SELECT COALESCE(SUM(ClaimAmount), 0)
                        FROM dbo.Claims
                    ) * 100.0
                    /
                    NULLIF(
                        (
                            SELECT COALESCE(SUM(PremiumAmount), 0)
                            FROM dbo.Policies
                        ),
                        0
                    )
                    AS DECIMAL(10, 2)
                )
        """)

        result = cursor.fetchone()

        if result[0] is None:
            return 0.0

        return float(result[0])

    finally:
        connection.close()

def get_policy_by_number(policy_number: str) -> dict:
    """
    Return information about a specific insurance policy.

    Args:
        policy_number: Business policy number, for example POL-12345.

    Returns:
        Dictionary containing policy information, or an error message
        if the policy does not exist.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                PolicyID,
                PolicyNumber,
                CustomerID,
                ProductID,
                AgentID,
                PremiumAmount,
                CoverageAmount,
                StartDate,
                EndDate,
                Status
            FROM dbo.Policies
            WHERE PolicyNumber = ?
            """,
            policy_number,
        )

        row = cursor.fetchone()

        if row is None:
            return {
                "found": False,
                "message": "Policy not found",
            }

        return {
            "found": True,
            "policy_id": row.PolicyID,
            "policy_number": row.PolicyNumber,
            "customer_id": row.CustomerID,
            "product_id": row.ProductID,
            "agent_id": row.AgentID,
            "premium_amount": float(row.PremiumAmount),
            "coverage_amount": float(row.CoverageAmount),
            "start_date": str(row.StartDate),
            "end_date": str(row.EndDate),
            "status": row.Status,
        }

    finally:
        connection.close()

def get_claim_by_id(claim_id: int) -> dict:
    """
    Retrieve detailed information about a specific insurance claim.

    Args:
        claim_id: Unique numeric identifier of the claim.

    Returns:
        Dictionary containing claim information, or an error message
        if the claim does not exist.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                ClaimID,
                PolicyID,
                ClaimNumber,
                ClaimDate,
                ClaimAmount,
                ApprovedAmount,
                Status,
                ClaimType,
                Description,
                FraudProbability,
                ProcessingDays
            FROM dbo.Claims
            WHERE ClaimID = ?
            """,
            claim_id,
        )

        row = cursor.fetchone()

        if row is None:
            return {
                "found": False,
                "message": "Claim not found",
            }

        return {
            "found": True,
            "claim_id": row.ClaimID,
            "policy_id": row.PolicyID,
            "claim_number": row.ClaimNumber,
            "claim_date": str(row.ClaimDate),
            "claim_amount": float(row.ClaimAmount),
            "approved_amount": (
                float(row.ApprovedAmount)
                if row.ApprovedAmount is not None
                else None
            ),
            "status": row.Status,
            "claim_type": row.ClaimType,
            "description": row.Description,
            "fraud_probability": (
                float(row.FraudProbability)
                if row.FraudProbability is not None
                else None
            ),
            "processing_days": row.ProcessingDays,
        }

    finally:
        connection.close()

def analyze_claim_risk(claim_id: int) -> dict:
    """
    Calculate deterministic risk indicators for a specific claim.

    This tool provides decision-support signals only.
    It does not determine whether a claim is fraudulent.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.ClaimID,
                c.PolicyID,
                c.ClaimNumber,
                c.ClaimDate,
                c.ClaimAmount,
                c.FraudProbability,
                c.ProcessingDays,
                p.CustomerID,
                p.PremiumAmount,
                p.CoverageAmount,
                p.StartDate
            FROM dbo.Claims c
            INNER JOIN dbo.Policies p
                ON c.PolicyID = p.PolicyID
            WHERE c.ClaimID = ?
            """,
            claim_id,
        )

        row = cursor.fetchone()

        if row is None:
            return {
                "found": False,
                "message": "Claim not found",
            }

        claim_amount = float(row.ClaimAmount)
        coverage_amount = float(row.CoverageAmount)

        fraud_probability = (
            float(row.FraudProbability)
            if row.FraudProbability is not None
            else 0.0
        )

        # How large is the claim relative to policy coverage?
        coverage_ratio = (
            claim_amount / coverage_amount
            if coverage_amount > 0
            else 0.0
        )

        # Days between policy start and claim.
        days_since_policy_start = (
            row.ClaimDate.date() - row.StartDate
        ).days

        risk_indicators = []

        if fraud_probability >= 0.70:
            risk_indicators.append(
                "High model-generated fraud risk score"
            )

        if coverage_ratio >= 0.50:
            risk_indicators.append(
                "Claim amount exceeds 50% of policy coverage"
            )

        if days_since_policy_start <= 30:
            risk_indicators.append(
                "Claim occurred within 30 days of policy start"
            )

        # Retrieve previous claims belonging to the same customer.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.Claims c
            INNER JOIN dbo.Policies p
                ON c.PolicyID = p.PolicyID
            WHERE p.CustomerID = ?
              AND c.ClaimID <> ?
            """,
            row.CustomerID,
            claim_id,
        )

        previous_claim_count = cursor.fetchone()[0]

        if previous_claim_count >= 3:
            risk_indicators.append(
                "Customer has three or more previous claims"
            )

        # Simple transparent prioritisation rule.
        indicator_count = len(risk_indicators)

        if indicator_count >= 3:
            review_priority = "High"
        elif indicator_count >= 1:
            review_priority = "Medium"
        else:
            review_priority = "Low"

        return {
            "found": True,
            "claim_id": row.ClaimID,
            "claim_number": row.ClaimNumber,
            "customer_id": row.CustomerID,
            "claim_amount": claim_amount,
            "coverage_amount": coverage_amount,
            "coverage_ratio": round(coverage_ratio, 4),
            "fraud_probability": fraud_probability,
            "days_since_policy_start": days_since_policy_start,
            "previous_claim_count": previous_claim_count,
            "risk_indicators": risk_indicators,
            "review_priority": review_priority,
            "disclaimer": (
                "Risk indicators are decision-support signals "
                "and require human review."
            ),
        }

    finally:
        connection.close()

def search_internal_knowledge(
    query: str,
    top_k: int = 3,
):
    """
    Search approved internal knowledge documents using
    semantic vector retrieval.

    Returns relevant document sections together with
    source metadata for traceability.
    """

    results = retrieve_knowledge(
        query=query,
        top_k=top_k,
    )

    return {
        "found": len(results) > 0,
        "query": query,
        "results": results,
    }
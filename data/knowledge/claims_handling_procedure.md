# Claims Handling Procedure

Document ID: DEMO-CLM-001
Version: 1.0
Classification: Internal - Demo
Purpose: Synthetic procedure created for the Insurance AI demonstration.

## 1. Purpose

This procedure defines the minimum review requirements for insurance
claims processed by the demonstration claims system.

The procedure is intended to ensure consistent claim assessment,
appropriate escalation, and human oversight of automated risk signals.

## 2. Initial Claim Review

Every submitted claim must be reviewed against the associated policy.

The reviewer must verify:

- the policy was active on the claim date;
- the claim occurred within the policy coverage period;
- the claimed amount does not exceed the policy coverage amount;
- the claim type is eligible for assessment under the policy.

A claim must not be rejected solely because an automated risk model
produces an elevated fraud probability.

## 3. Early Claims

A claim occurring within 30 days of the policy start date is classified
as an Early Claim.

Early Claims require additional human review before a final approval
or rejection decision is made.

The early-claim indicator alone is not sufficient grounds for rejection.

## 4. Fraud Risk Indicators

Fraud probability is a decision-support signal.

The following review levels apply:

- Fraud probability below 0.20: Low model risk.
- Fraud probability from 0.20 to below 0.50: Medium model risk.
- Fraud probability of 0.50 or greater: High model risk.

No claim may be automatically rejected solely because of its fraud
probability.

Claims with High model risk must be escalated for specialist human review.

## 5. Rejected Claims

A rejected claim must contain:

- a documented rejection reason;
- evidence supporting the rejection decision;
- confirmation that policy coverage was checked;
- confirmation that applicable risk indicators were reviewed.

For an Early Claim, the record must additionally show that the required
human review occurred before rejection.

If these records are unavailable, compliance with the rejection procedure
cannot be confirmed.

## 6. Processing Time

Claims should normally be processed within 30 calendar days.

Claims exceeding 30 days require a documented explanation for the delay.

Processing time alone must not determine whether a claim is approved
or rejected.

## 7. Human Oversight

AI-generated risk scores, fraud probabilities, recommendations, and
other automated indicators are decision-support information only.

Final claim approval and rejection decisions require human accountability.

## 8. Auditability

The claims system should retain sufficient information to reconstruct
the basis of a decision, including:

- claim information;
- policy information;
- risk indicators used during assessment;
- rejection or approval rationale;
- human review or approval records.

The absence of required evidence must be reported as missing information
rather than inferred by an AI system.
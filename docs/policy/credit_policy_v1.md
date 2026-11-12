# Credit Policy v1: BNPL Underwriting

**Version:** 1.0 | **Market:** Saudi Arabia | **Currency:** SAR | **Status:** Draft (simulation project)

> All numbers are starting assumptions for a simulated environment. Every rule has an ID
> (`POL-x.x`) so the rules engine, the policy-RAG agent, and the evals can cite it.
> Regulatory points (SAMA rules, Sharia treatment of fees) must be verified against current
> official sources before being treated as correct.

---

## 1. Products (POL-1)

| ID | Product | Installments | Tenor | Min basket | Max basket |
|---|---|---|---|---|---|
| POL-1.1 | Pay in 3 | 3 equal (today, +30d, +60d) | 60 days | 50 | 3,000 |
| POL-1.2 | Pay in 4 | 4 equal (today, +2w, +4w, +6w) | 6 weeks | 50 | 2,000 |
| POL-1.3 | Installments 6M | 6 equal monthly | 6 months | 500 | 5,000 |

- POL-1.4: The customer always pays the **cash price** of the goods. No interest, no markup (see POL-8).
- POL-1.5: Installments 6M is available only to customers with at least 1 completed on-time order, or PD band A.

---

## 2. Eligibility, hard requirements (POL-2)

An application or checkout failing any rule below is declined without scoring.

| ID | Rule | Reason code |
|---|---|---|
| POL-2.1 | Age 18 or older | `R01_UNDERAGE` |
| POL-2.2 | National ID or Iqama verified (identity check passed) | `R02_ID_NOT_VERIFIED` |
| POL-2.3 | Saudi mobile number verified by OTP | `R03_PHONE_NOT_VERIFIED` |
| POL-2.4 | No sanctions or watchlist match | `R04_SANCTIONS_HIT` |
| POL-2.5 | No confirmed fraud flag on the customer | `R05_CONFIRMED_FRAUD` |
| POL-2.6 | No open order more than 30 days overdue | `R06_SEVERE_DELINQUENCY` |
| POL-2.7 | Bureau score at or above minimum (`MIN_BUREAU_SCORE = 550`), when a bureau record exists | `R07_LOW_BUREAU_SCORE` |
| POL-2.8 | Active (unpaid) orders at most 3 | `R08_TOO_MANY_ACTIVE_ORDERS` |
| POL-2.9 | Merchant is active and not blocked | `R09_MERCHANT_BLOCKED` |

---

## 3. Risk model and score bands (POL-3)

- POL-3.1: **Default definition:** an order is "bad" if any installment is 60+ days past due within 120 days of the order date.
- POL-3.2: The PD model outputs a **calibrated** probability of default. Calibration is checked on every model release.
- POL-3.3: Score bands are applied after the hard rules in POL-2.

| Band | PD range | Action | Reason code (when not full approval) |
|---|---|---|---|
| A | PD < 3% | Auto-approve | none |
| B | 3% to < 8% | Approve with reduced limit and/or step-up verification | `R20_MODERATE_RISK` |
| C | 8% to < 15% | Refer to human underwriter | `R21_REFER_HIGH_RISK` |
| D | 15% or more | Auto-decline | `R22_HIGH_RISK` |

- POL-3.4: **Thin file** customers (no bureau record and fewer than 2 completed orders) are capped at Band B actions and the new-customer limit.
- POL-3.5: Protected attributes (gender, nationality, religion, etc.) must never be model features or rule inputs.

---

## 4. Credit limits (POL-4)

| ID | Rule |
|---|---|
| POL-4.1 | New customer starting limit: 300 to 3,000 SAR, assigned by PD band (A up to 3,000; B up to 1,000; thin file default 500). |
| POL-4.2 | Maximum single basket: 5,000 SAR (product maximums in POL-1 also apply). |
| POL-4.3 | Available limit = assigned limit minus outstanding balance of active orders. |
| POL-4.4 | Basket larger than available limit is declined with `R30_EXCEEDS_LIMIT`, or offered a smaller basket or higher down payment. |
| POL-4.5 | Per-merchant exposure cap: no more than 40% of the customer limit at one merchant within 7 days. |
| POL-4.6 | High-risk categories (electronics, gift cards, jewelry) are capped at 50% of the available limit and always get step-up if order is above 1,500 SAR. |

---

## 5. Step-up verification (POL-5)

- POL-5.1: Step-up = extra verification (OTP re-check, selfie liveness, or national authentication).
- POL-5.2: Triggered by: Band B on baskets above 1,000 SAR; new device on an existing account with a high-value basket; moderate fraud score (see POL-6).
- POL-5.3: Failing or abandoning step-up results in decline with `R40_STEPUP_FAILED`.

---

## 6. Fraud and velocity rules (POL-6)

| ID | Rule | Action | Reason code |
|---|---|---|---|
| POL-6.1 | More than 3 orders in 1 hour | Step-up | `R50_VELOCITY_1H` |
| POL-6.2 | More than 6 orders in 24 hours | Refer | `R51_VELOCITY_24H` |
| POL-6.3 | One device linked to more than 3 customer accounts | Refer | `R52_SHARED_DEVICE` |
| POL-6.4 | One phone or address shared by more than 3 customers | Refer | `R53_SHARED_IDENTIFIER` |
| POL-6.5 | Account younger than 24 hours with basket above 1,500 SAR | Step-up | `R54_NEW_ACCOUNT_HIGH_VALUE` |
| POL-6.6 | Fraud model score above `FRAUD_BLOCK` threshold | Decline | `R55_FRAUD_SUSPECTED` |

Fraud-related decline reasons are **internal**. Customer-facing messages must be generic (see POL-10).

---

## 7. Limit management (POL-7)

| ID | Trigger | Action |
|---|---|---|
| POL-7.1 | 3 consecutive on-time orders | Increase limit by 20% (up to POL-4.2 cap) |
| POL-7.2 | Any installment 7+ days late | Freeze limit increases; block Installments 6M |
| POL-7.3 | Any installment 30+ days late | Reduce limit by 50% and block new orders until cleared |
| POL-7.4 | 60+ days late (default) | Block account; send to collections |
| POL-7.5 | Limit review run | Monthly batch review; every change logged with reason |
| POL-7.6 | Limit increases above 5,000 SAR total | Human approval required |

---

## 8. Pricing and Sharia treatment (POL-8)

> Verify with a qualified Sharia scholar and current SAMA rules before production use.

| ID | Rule |
|---|---|
| POL-8.1 | **No interest or markup charged to the customer.** Customer pays the cash price in installments. |
| POL-8.2 | Revenue comes from the **merchant fee** (2% to 6% of order value by category tier). |
| POL-8.3 | Late fee is a flat amount with a cap (for example 5% of order value or 75 SAR, whichever is lower). |
| POL-8.4 | **Late fees are not recognized as company revenue.** They are recorded separately and routed to charity (or limited to actual recovery cost, per Sharia board guidance). |
| POL-8.5 | No compounding of fees, and no fee on fees. |
| POL-8.6 | Prohibited merchant categories (for example alcohol, gambling, adult content, tobacco) are blocked: `R09_MERCHANT_BLOCKED` and `R60_PROHIBITED_CATEGORY`. |
| POL-8.7 | Pricing and expected profit calculations must be done in code, never by an LLM. |

---

## 9. Referral and human review (POL-9)

| ID | Rule |
|---|---|
| POL-9.1 | Band C, fraud refer rules (POL-6.2 to 6.4), and conflicting data go to the human review queue. |
| POL-9.2 | Reviewer decisions: approve, approve with lower limit, decline. A reason is mandatory. |
| POL-9.3 | Referral SLA target: 1 business day (async; the checkout shows "under review"). |
| POL-9.4 | The AI agent may prepare a recommendation. It may **not** finalize decisions on Band C or any fraud refer. |
| POL-9.5 | Agents may auto-resolve only low-risk referrals where all verification checks passed (to be tuned in Phase 3). |
| POL-9.6 | All overrides are stored with reviewer ID, timestamp, and reason for retraining and audit. |

---

## 10. Decision messages and explainability (POL-10)

- POL-10.1: Every decision stores: inputs, features, PD, fraud score, rule hits, reason codes, model version, rule version, latency.
- POL-10.2: Customer-facing declines show at most 2 plain-language reasons and never expose fraud logic.
- POL-10.3: The explanation text must match the reason codes in the decision record (checked in evals).
- POL-10.4: Reason codes from the ML model come from SHAP and are mapped to the codes in section 11.

---

## 11. Reason code catalog

| Code | Meaning | Customer-facing |
|---|---|---|
| `R01_UNDERAGE` | Under minimum age | Yes |
| `R02_ID_NOT_VERIFIED` | Identity not verified | Yes |
| `R03_PHONE_NOT_VERIFIED` | Phone not verified | Yes |
| `R04_SANCTIONS_HIT` | Sanctions match | No (generic) |
| `R05_CONFIRMED_FRAUD` | Confirmed fraud | No (generic) |
| `R06_SEVERE_DELINQUENCY` | Overdue 30+ days | Yes |
| `R07_LOW_BUREAU_SCORE` | Bureau score too low | Yes |
| `R08_TOO_MANY_ACTIVE_ORDERS` | Too many open orders | Yes |
| `R09_MERCHANT_BLOCKED` | Merchant not allowed | Yes |
| `R20_MODERATE_RISK` | Moderate risk, reduced terms | Yes |
| `R21_REFER_HIGH_RISK` | Needs manual review | Yes ("under review") |
| `R22_HIGH_RISK` | Risk above appetite | Yes (generic) |
| `R30_EXCEEDS_LIMIT` | Basket above available limit | Yes |
| `R31_HIGH_UTILIZATION` | Limit heavily used | Yes |
| `R32_RECENT_LATE_PAYMENT` | Recent late payment | Yes |
| `R40_STEPUP_FAILED` | Extra verification failed | Yes |
| `R50_VELOCITY_1H` | Too many orders in 1 hour | No |
| `R51_VELOCITY_24H` | Too many orders in 24 hours | No |
| `R52_SHARED_DEVICE` | Device shared across accounts | No |
| `R53_SHARED_IDENTIFIER` | Shared phone or address | No |
| `R54_NEW_ACCOUNT_HIGH_VALUE` | New account, high basket | No |
| `R55_FRAUD_SUSPECTED` | Fraud model flag | No |
| `R60_PROHIBITED_CATEGORY` | Prohibited merchant category | Yes |

---

## 12. Operational controls (POL-12)

- POL-12.1: **Kill switch:** if the model service is unavailable, fall back to conservative rules: approve only returning on-time customers up to 500 SAR, step-up for the rest, and log `FALLBACK_MODE`.
- POL-12.2: **Circuit breakers:** maximum auto-approvals per hour and maximum exposure per segment; breach pauses auto-approval for the segment.
- POL-12.3: **Shadow mode:** new models and policies run in shadow before replacing the champion.
- POL-12.4: **Versioning:** this document, the rules YAML, the model, and agent prompts each have a version, and every decision records all of them.
- POL-12.5: **Fairness monitoring:** approval and default rates tracked across groups using held-out attributes (never used as inputs).

---

## 13. Change log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-12 | Initial draft |

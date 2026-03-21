# Skill Pack: Valuation

> Inject into a project at bootstrap with `--skill valuation`, or manually append to an existing project's `SKILL.md`.
> Appended to SKILL.md. Also enables valuation-specific sections in CLAUDE.md and SPEC.md.

---

## Valuation Procedures

### DCF Valuation Template
```
Inputs:
  - Free Cash Flows (FCF) for explicit forecast period
  - Terminal growth rate (g) — use GDP growth or lower; never > WACC
  - WACC (Weighted Average Cost of Capital)
  - Net debt (or net cash)
  - Shares outstanding

Formula:
  EV = Σ [FCF_t / (1+WACC)^t] + [FCF_n*(1+g) / (WACC-g)] / (1+WACC)^n
  Equity Value = EV - Net Debt
  Price per Share = Equity Value / Shares Outstanding

Validation:
  - WACC > g (terminal value formula breaks otherwise)
  - FCF series signed correctly (positive = cash in)
  - Required: sensitivity table — WACC ±100bps, g ±50bps
```

### NAV Appraisal Template
```
Inputs:
  - Asset schedule with individual valuations
  - Liability schedule (debt, obligations)
  - Adjustments (unrealized gains/losses, off-balance-sheet items)

Formula:
  NAV = Σ(Asset Values) - Σ(Liabilities) + Adjustments

Validation:
  - Cross-check asset values against market comparables where available
  - Flag Level 3 inputs (unobservable) — apply illiquidity discount per policy
```

### Sensitivity Analysis Standard
```
For every key assumption A with base value A_0:
  Bear:  A_0 - 1σ (or defined stress)
  Base:  A_0
  Bull:  A_0 + 1σ (or defined upside)

Output: table with rows=assumption, columns=output metric
Never present a single-point estimate without this table.
```

---

## Financial Precision — Code Patterns

### Monetary Arithmetic (Python)
```python
from decimal import Decimal, ROUND_HALF_UP

def to_decimal(value: float | str | int) -> Decimal:
    """Convert to Decimal for monetary calculations. Never use float for money."""
    return Decimal(str(value))

def round_currency(value: Decimal, places: int = 2) -> Decimal:
    return value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
```

---

## Financial Conventions (add to SPEC.md)

- **Currency**: [specify]
- **Reference Date**: [specify]
- **Valuation Methodology**: [DCF / NAV / Comparable Transactions]
- **Discount Rate Source**: [specify]
- **Key Assumptions**: [list]
- Monetary values stored as `Decimal`, never `float`
- Dates in ISO 8601 (`YYYY-MM-DD`)
- Rates as decimals in code (`0.085`), formatted as % in display layer

---

## Valuation Output Requirements

Every valuation output must include:
1. Point estimate (or range)
2. Confidence interval / scenario range
3. Methodology used
4. Key assumptions (explicitly labelled as fact / estimate / assumption)
5. Sensitivity table on the two most impactful inputs

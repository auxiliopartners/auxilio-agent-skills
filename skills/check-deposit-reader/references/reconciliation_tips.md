# Reconciliation Tips

Guidance for matching extracted check data against donation tracking records.

## Common matching strategies

### Match by amount + date
The simplest approach: match check amount and date to donation records.
Works well when amounts are unique. For duplicate amounts on the same date,
use payer name as a tiebreaker.

### Match by payer name
Normalize names before matching (strip middle initials, handle "Bob" vs
"Robert", etc.). Bill-pay checks sometimes show a different name variant
than what's in the donation system.

### Match by check number
If the donation system tracks check numbers, this is the most reliable
match key. Check numbers are unique per bank account.

## Handling bill-pay checks with no payer name

When the Account field shows "PAYMENT" or "NO ACCOUNT NUMBER":

1. Try matching by amount + date to narrow candidates
2. Look at the routing/account number in the MICR line — if you have
   prior checks from the same account, the payer may be the same
3. Flag for manual review if no confident match is found

## Cash deposits

Cash deposits (CASH IN - DEBIT) typically represent loose cash collected
in offering plates or donation boxes. These usually don't map to individual
donors. Common approaches:

- Record as "Anonymous Cash" in the donation system
- Aggregate multiple cash deposits by date
- Match to a general "Cash Donations" fund/category

## Output format for reconciliation

When reconciling, produce a report showing:

| Check | Payer | Amount | Date | Match Status | Matched Record |
|-------|-------|--------|------|--------------|----------------|
| 001   | Name  | $300   | 1/27 | Matched      | Donation #1234 |
| 005   | (none)| $1,335 | 1/16 | Needs Review | —              |

Statuses: Matched, Needs Review, No Match, Cash Deposit

---
name: check-deposit-reader
description: >
  Extract structured data from scanned check deposit PDFs. Reads payer name,
  address, phone, email, payee, amount, date, check number, and memo from
  bank check images. Handles personal checks, bill-pay remittance checks,
  and cash deposit slips. Use this skill whenever the user uploads a PDF of
  scanned checks, mentions check deposits, check images, bank deposit scans,
  or wants to reconcile check deposit data. Also trigger when the user asks
  to read, OCR, or extract data from checks, or when processing donation
  deposit records.
---

# Check Deposit Reader

Extract structured payment data from scanned check deposit PDFs. These PDFs
typically come from bank imaging systems and contain front-and-back scans of
deposited checks arranged in a grid layout, sometimes several per page.

## When to use this skill

Trigger on any of these signals:

- User uploads a PDF of scanned checks or mentions "check images" / "check scans"
- User wants to extract payer/payee/amount data from check deposits
- User mentions reconciling check deposits against donation records
- User asks to read, OCR, or parse check images
- User mentions bank deposit scans, deposit slips, or check reconciliation

## How it works

The extraction uses a two-phase approach:

1. **Segmentation** — A Python script (`scripts/extract_checks.py`) converts
   each PDF page to images, detects individual check regions using contour
   analysis, runs OCR, and saves everything into a working directory.

2. **Visual extraction** — You (Claude) examine each check image using your
   vision capability, cross-reference with OCR text, and produce structured
   JSON and CSV output for each check.

This two-phase design matters because OCR alone is unreliable on handwritten
checks and complex bank layouts, but provides useful supplementary data —
especially for MICR line numbers and machine-printed fields.

## Step 1: Run the segmentation script

```bash
python3 <skill_path>/scripts/extract_checks.py "<input_pdf>" "<output_dir>" --dpi 300
```

- `<input_pdf>` — the uploaded check scan PDF
- `<output_dir>` — a working directory (e.g., `./check_extraction/`)

The script installs its own dependencies and produces:

- `page_N.png` — full page images
- `check_NNN.png` — cropped individual check/deposit images
- `check_NNN_ocr.txt` — Tesseract OCR text for each item
- `check_NNN_payer_detail.png` — **zoomed 2x crop of the payer region** (top-left of check)
- `check_NNN_payer_ocr.txt` — OCR of the zoomed payer region
- `check_NNN_amount_detail.png` — zoomed 2x crop of the amount/date region (top-right)
- `check_NNN_amount_ocr.txt` — OCR of the zoomed amount region
- `manifest.json` — metadata including auto-detected document type and detail crop info

If the script fails (unusual layout), fall back to viewing the full page
image and manually identifying checks.

## Step 2: Examine each check image

For each entry in `manifest.json`:

1. **View the payer detail crop first** (`_payer_detail.png`) — this 2x-upscaled
   image of the top-left region is where payer name, address, and phone live.
   On bill-pay checks especially, this text is often very small in the full
   check image but readable in the zoomed crop.
2. **Read the payer OCR** (`_payer_ocr.txt`) for supplementary text.
3. **View the full check image** (`check_NNN.png`) for overall context, payee,
   memo, and any fields not in the detail crops.
4. **Read the full OCR** (`_ocr.txt`) for MICR line numbers and deposit strip data.
5. Optionally view `_amount_detail.png` if the amount or date is unclear.

### Fields to extract

| Field | Where to find it |
|---|---|
| **Payer name** | Upper-left of personal checks. On bill-pay checks, the "Account:" line at top, or the name/address block on the left. |
| **Payer address** | Below payer name: street, city, state, ZIP — typically 2-3 lines. |
| **Payer phone** | Sometimes below address or in "Direct Any Questions To" section. Often absent. |
| **Payer email** | Rarely present. Only extract if clearly visible. |
| **Payee name** | After "Pay to the order of" or "TO / THE ORDER OF". |
| **Check amount** | Numerical amount in the amount box AND the written-out dollar line. Cross-check these match. |
| **Check date** | Upper-right area of the check. |
| **Check number** | Upper-right corner (personal) or header area (bill-pay). Confirm against MICR line at bottom. |
| **Check memo** | Lower-left, after "MEMO:" or "For:". |

### Handling payer names

Checks often list one or two people (e.g., a married couple or business
partners). When there are two name lines, follow these conventions:

- **Record both names** in the `payer_name` field, separated by " & "
  (e.g., "Robert John March II & Carolyn T March").
- **Infer shared last names**: If the second name shows only a first/middle
  and initial but no last name, they almost certainly share the last name of
  the first person. For example, if line 1 is "ROBERT JOHN MARCH II" and
  line 2 is "CAROLYN T MARCH", the last name is "March" for both.
- **Suffixes and titles**: Watch for suffixes like II, III, Jr., Sr. that
  may appear after the last name. Include them in the name as written. OCR
  sometimes misreads "II" as "H", "11", or "Il" — use context and the zoomed
  image to verify.
- **Business names**: Sometimes the payer is a business, foundation, trust,
  or estate rather than a person. Record the full entity name as-is.
- **Name normalization**: Preserve the name exactly as printed. Do not
  reformat capitalization (some checks print in ALL CAPS — that's fine to
  record as-is, or you can normalize to title case if the user requests it).

### Reading tips

- **Cross-reference vision with OCR**: Read the image first, then check
  the OCR text for any details you might have missed (especially numbers).
- **MICR line**: The magnetic ink line at the very bottom of a check
  contains the routing number, account number, and check number. The OCR
  text sometimes captures this when the image is hard to read.
- **Handwritten fields**: For handwritten amounts, dates, and payee names,
  trust your visual reading over OCR. Note any uncertainty.
- **Deposit verification strip**: Many check images include a printed strip
  below the check with the deposit date, check number, and amount — use
  this to cross-verify your extraction.

## Step 3: Handle different check types

### Personal checks
Standard checks with pre-printed payer name and address in upper-left.
Check number in upper-right. May have handwritten amounts, dates, payees.

### Bill-pay / remittance checks
Bank-issued on behalf of a payer. Key traits:

- Header: "PLEASE POST THIS PAYMENT FOR OUR MUTUAL CUSTOMER"
- "Account:" line at top shows payer name (or sometimes "PAYMENT" / "NO ACCOUNT NUMBER")
- Payer address in the left block
- Machine-printed, not handwritten
- May include "Questions To" phone number

Even when the Account field shows "PAYMENT" or "NO ACCOUNT NUMBER", the
**payer name and address are almost always printed below the Account line**
in the top-left block of the check. This text is often small and hard to read
in the full check image — always check the `_payer_detail.png` zoomed crop
and `_payer_ocr.txt` first. The payer block may contain one or two personal
names (e.g., "ROBERT JOHN MARCH" / "CAROLYN T MARCH") or a business name.

If the payer name is still not visible after checking the zoomed crop, then
note it for manual identification.

### Cash deposit slips
Labeled "CASH IN - DEBIT" — these represent cash deposits, not checks.

- Extract the amount and date
- Note account number and cash drawer ID
- No payer — leave payer fields as null
- Flag as `cash_deposit` type

### Back-of-check images
Many scans include the check's back (endorsement stamps). These are NOT
separate checks. Look for deposit stamps, dates, and bank info. Note
relevant details on the corresponding front-side record.

## Step 4: Produce structured output

Create `extracted_checks.json` in the output directory:

```json
[
  {
    "check_id": "check_001",
    "type": "personal_check | bill_pay_check | cash_deposit",
    "payer_name": "Full Name",
    "payer_address": "Full address on one line",
    "payer_phone": "Phone number",
    "payer_email": null,
    "payee_name": "Payee name",
    "check_amount": 300.00,
    "check_date": "YYYY-MM-DD",
    "check_number": "Number as string",
    "check_memo": "Memo text",
    "bank": "Issuing bank name",
    "notes": "Observations, uncertainties, special circumstances"
  }
]
```

Output rules:

- Use `null` for genuinely absent fields. Never guess or fabricate.
- Amounts are numbers (no currency symbols).
- Dates are ISO 8601: `YYYY-MM-DD`.
- Check numbers are strings (may have leading zeros).
- For partially legible fields, include your best reading and explain
  the uncertainty in `notes`.
- Back-of-check images do NOT get separate records.

Also create `extracted_checks.csv` with headers:

```
check_id,type,payer_name,payer_address,payer_phone,payer_email,payee_name,check_amount,check_date,check_number,check_memo,bank,notes
```

## Step 5: Present results

Summarize for the user:

- Total checks found and types breakdown
- Checks with complete payer information vs. those needing manual review
- Any items flagged for attention (unclear fields, missing payer, cash deposits)
- Link to the JSON and CSV output files

If the user wants to reconcile against donation records, offer to help
match — see `references/reconciliation_tips.md`.

## Troubleshooting

- **No regions detected**: Increase `--dpi` to 400, or view the full page
  image and segment manually.
- **Very poor OCR**: Expected for handwritten checks. Rely on vision.
  OCR is supplementary.
- **Checks overlap or cut off**: Note in `notes` field, extract what's visible.
- **Multi-page PDFs**: Handled automatically by the script.

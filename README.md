# LedgerData

LedgerData is a desktop application for automated financial reconciliation and accounting validation using Excel-based datasets.

The system compares DIOT records against accounting files for VAT (IVA), IEPS, and non-deductible transactions (227), detecting discrepancies and generating reconciliation reports automatically.

## Features

- Automated reconciliation by CEGAP
- Excel file processing
- DIOT validation
- IVA validation
- IEPS validation
- 227 validation
- Difference detection
- Automatic Excel export
- Desktop interface with drag and drop support
- Cross-platform support (Windows/Linux)

## Technologies

- Python
- Pandas
- PySide6
- OpenPyXL

## Project Structure

```text
app/
├── core/
├── parsers/
├── ui/
├── main.py
```

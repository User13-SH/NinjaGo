# Care Observations prototype

Single-file HTML prototype for the Care Observations feature: observation list, charts, trend explorer, observation form, Mark In-Error dialog, and the record page with Related and Details tabs.

## Files

- `care-observations.html` - the prototype. Open it directly in a browser; there is no build step.
- `tests/regression.py` - Playwright (Python) regression script covering the list, filter, form, chart, record and dialog flows at several widths.

## Running the regression script

```
pip install playwright
playwright install chromium
python3 tests/regression.py
```

The script loads the prototype from a local path. Edit the path inside the script if the prototype is in a different folder.

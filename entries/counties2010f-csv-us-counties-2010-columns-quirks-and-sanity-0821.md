---
id: counties2010f-csv-us-counties-2010-columns-quirks-and-sanity-0821
kind: convention
title: 'Counties2010f.csv (US counties 2010): columns, quirks and sanity values'
domain:
- dataviz
- datasets
stack: {}
symptoms:
- Working with Counties2010f.csv in the Info-vis course
- Per-state SD / correlation undefined for District of Columbia
- First column name looks wrong (UTF-8 BOM)
root_cause: ''
fix: 'Load with `FileAttachment("Counties2010f.csv").csv({typed: "auto"})`. 3,139 county rows over 51
  ''states'' (50 + DC). Columns: Name, State (2-letter), StateName, FullName, FIPS, Latitude, Longitude,
  Population, Pop2000, IncomePerCapita, PercentCollegeGrad, MedianRent, CommuteTime, LandArea. The file
  starts with a UTF-8 BOM, which only affects the first column name (Name). IncomePerCapita, PercentCollegeGrad
  and Population have no blanks. DC has 1 county (per-state SD and r undefined: drop it); Delaware has
  3 (r ≈ 0.9995).'
failed_attempts: []
verify: 'Alabama: mean income ≈ $27,664, mean college ≈ 15.2%, population 4,779,736, 67 counties. Within-state
  r(college %, income) ranges 0.19 (ND) to 1.00 (DE), all positive; CA 0.92, NY 0.80, TX 0.50.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Counties2010f.csv (US counties 2010): columns, quirks and sanity values

> [!note] convention · unverified · used 0×, failed 0×
> #dataviz #datasets #kind/convention #status/unverified

## Symptoms
```text
Working with Counties2010f.csv in the Info-vis course
Per-state SD / correlation undefined for District of Columbia
First column name looks wrong (UTF-8 BOM)
```

## Convention
Load with `FileAttachment("Counties2010f.csv").csv({typed: "auto"})`. 3,139 county rows over 51 'states' (50 + DC). Columns: Name, State (2-letter), StateName, FullName, FIPS, Latitude, Longitude, Population, Pop2000, IncomePerCapita, PercentCollegeGrad, MedianRent, CommuteTime, LandArea. The file starts with a UTF-8 BOM, which only affects the first column name (Name). IncomePerCapita, PercentCollegeGrad and Population have no blanks. DC has 1 county (per-state SD and r undefined: drop it); Delaware has 3 (r ≈ 0.9995).

## Verify
Alabama: mean income ≈ \$27,664, mean college ≈ 15.2%, population 4,779,736, 67 counties. Within-state r(college %, income) ranges 0.19 (ND) to 1.00 (DE), all positive; CA 0.92, NY 0.80, TX 0.50.

<small>created 2026-10-06 · id `counties2010f-csv-us-counties-2010-columns-quirks-and-sanity-0821`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent).

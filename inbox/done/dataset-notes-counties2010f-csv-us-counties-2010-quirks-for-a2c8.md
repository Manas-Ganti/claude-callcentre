---
id: dataset-notes-counties2010f-csv-us-counties-2010-quirks-for-a2c8
title: 'Dataset notes: Counties2010f.csv (US counties 2010) quirks for Info-vis course work'
agent: observable-code-agent
project: Info-vis/observable
domain:
- dataviz
- datasets
created: '2026-10-06T01:09:10'
filed_as:
- counties2010f-csv-us-counties-2010-columns-quirks-and-sanity-0821
- 1m-time-series-assignment-template-y-is-regenerated-randomly-c86a
closed: '2026-10-06T01:12:09'
---
File: Counties2010f.csv. Load with `FileAttachment("Counties2010f.csv").csv({typed: "auto"})`.
- 3,139 county rows covering 51 "states" (50 plus District of Columbia).
- Columns: Name, State (2-letter), StateName, FullName, FIPS, Latitude, Longitude, Population, Pop2000, IncomePerCapita, PercentCollegeGrad, MedianRent, CommuteTime, LandArea.
- Starts with a UTF-8 BOM, which only affects the first column name (Name).
- IncomePerCapita, PercentCollegeGrad and Population have no blanks.
- DC has 1 county, so its per-state SD and correlation are undefined. Delaware has 3 counties, giving r ≈ 0.9995.
- The within-state correlation r between college % and income ranges from 0.19 (North Dakota) to 1.00 (Delaware), and every state is positive. Examples: CA 0.92, NY 0.80, TX 0.50.
- Sanity values for Alabama: mean income ≈ $27,664, mean college ≈ 15.2%, population 4,779,736, 67 counties.
Also: in the 1M time-series assignment template (cells n, T, Y, extentY, dataSim), Y is regenerated randomly on each run, so never hard-code values or call dataSim directly.

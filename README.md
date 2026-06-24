# IDX Exchange MLS Analytics

Data analyst internship project analyzing Southern California MLS transaction data from CRMLS (California Regional Multiple Listing Service).

## Overview
This repository contains Python scripts for processing and analyzing monthly MLS listing and sold transaction data. The final deliverable is two interactive Tableau dashboards covering market analysis and competitive intelligence.

## Objectives
- Aggregate monthly MLS listing and sold transaction data into unified datasets
- Clean and validate raw MLS data including date consistency and geographic checks
- Enrich datasets with 30-year fixed mortgage rate data from FRED
- Engineer key housing market metrics including price ratios, price per square foot, and days on market
- Detect and handle outliers using statistical methods
- Build interactive Tableau dashboards for market trend analysis and competitive intelligence
- Produce a 1-page market intelligence report and 5-minute presentation

## Data
- Source: CRMLS via CoreLogic Trestle API
- Coverage: January 2024 through May 2026
- Residential listings: 591,977 rows
- Residential sold transactions: 430,635 rows

## Tools
- Python (pandas)
- Tableau Public

# Childhood Care, Stability and Opportunity in South Africa

An ethical, data-driven portfolio project examining how children's living arrangements, household resources, caregiver context and exposure to hardship are associated with education and wellbeing outcomes in South Africa.

**Interactive dashboard:** [Childhood Care, Stability and Opportunity in South Africa](https://blessiie-10.github.io/Childhood-Care-Stability-Opportunity-SA/)

## Research question

How are children's parent co-residence, household resources, caregiver stability and exposure to adversity associated with education and wellbeing outcomes in South Africa?

## Personal motivation

This project is rooted in my own experience of growing up as a foster child. I saw that children raised in different household circumstances can face very different levels of stability, support and opportunity. Some foster children I observed struggled to remain in school or became exposed to substance use, often within difficult household environments.

I wanted to move beyond assumptions and use data to compare the experiences of children living with both biological parents, a mother only, a father only or neither biological parent. The aim is not to label one family structure as better than another, but to understand how household resources, caregiver stability and access to support are associated with children's outcomes.

## Why this project matters

South African children grow up in many different family and care arrangements. This project does not rank biological, foster, adoptive or extended families. It focuses on the conditions that can support or constrain children: stable care, education access, food security, healthcare, social protection and household resources.

## Main dataset

The primary dataset is the [Statistics South Africa General Household Survey 2025](https://www.datafirst.uct.ac.za/dataportal/index.php/catalog/1144), a nationally representative household survey covering education, health, social development, housing, services, food security and household resources.

The initial analysis uses four observable parent co-residence groups:

1. Lives with both biological parents
2. Lives with mother only
3. Lives with father only
4. Lives with neither biological parent

These are living-arrangement categories, not measures of care quality.

## Planned outcomes

* School attendance for school-age children
* Grade repetition
* Early childhood development attendance where applicable
* Self-reported health
* Child-support and foster-care grant receipt
* Household food insecurity
* Household income, services and selected assets

## Important interpretation rules

* Association does not prove causation.
* Outcomes are reported as measurable indicators, not a single score of "success".
* The GHS does not directly identify adopted children.
* Foster-care grant receipt is not a complete identifier for all children in foster care.
* Discipline indicators for young children will be analysed descriptively and will not be labelled as abuse unless the source supports that definition.
* Small groups and provincial estimates will be checked for sample-size and precision concerns.

## Project structure

```text
data/raw/          Locally downloaded GHS files; not committed
data/processed/    Analysis-ready data; not committed
data/reference/    Source, variable, and published-baseline trackers
docs/              Project scope and methodology
notebooks/         Step-by-step analysis notebooks
src/               Reusable Python scripts
outputs/figures/   Exported charts
outputs/tables/    Exported summary tables
```



## Published 2025 baseline

Stats SA reports that 45.9% of children lived with their mothers only, 31.4% with both parents, 18.5% with neither parent and 4.2% with their fathers only in 2025. These published figures will be used to validate the weighted grouping logic before further analysis.

## Current status

* \[x] Research question refined
* \[x] Ethical safeguards defined
* \[x] GHS 2025 selected as the primary dataset
* \[x] Source and variable trackers created
* \[x] Data-inspection and child-file scripts prepared
* \[x] GHS 2025 microdata added locally
* \[x] Weighted living-arrangement results validated
* \[x] First education, social-protection, and food-security comparisons completed
* \[x] Household context profiles completed
* \[x] Adjusted education point estimates completed
* \[x] Design-aware confidence intervals completed for observed education estimates
* \[x] Initial and adjusted findings written
* \[x] Interactive portfolio dashboard completed
* \[x] Eight-slide portfolio presentation completed
* \[ ] Formal inference for adjusted model contrasts completed

## Results to date

* [Initial weighted findings](docs/initial_findings.md)
* [Adjusted education findings](docs/adjusted_findings.md)
* [Methodology and limitations](docs/methodology.md)
* [Dashboard and presentation guide](docs/dashboard_and_presentation.md)
* [Portfolio presentation](outputs/Childhood-Care-Stability-Opportunity-SA-Presentation.pptx)

## Data citation

Statistics South Africa. *General Household Survey 2025* \[dataset], Version 1. Pretoria: Statistics South Africa \[producer], 2026. Cape Town: DataFirst \[distributor], 2026. [DOI: 10.25828/a4a6-p161](https://doi.org/10.25828/a4a6-p161).


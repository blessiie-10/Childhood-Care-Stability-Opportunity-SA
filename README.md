# Childhood Care, Stability and Opportunity in South Africa

An ethical, data-driven portfolio project exploring how children’s living arrangements and household conditions are associated with education, food security, social protection, and access to opportunity in South Africa.

**Explore the project:** [Interactive dashboard](https://childhood-care-sa.singo-blessing10.chatgpt.site) · [Portfolio presentation](outputs/Childhood-Care-Stability-Opportunity-SA-Presentation.pptx)

## Why I chose this project

This project began with my own experience of growing up as a foster child.

While growing up, I saw some fostered children around me struggle at school, leave school early, or become involved with drugs. I also saw that these experiences were closely connected to the households and communities in which children were growing up: the stability of their care, the resources available at home, food security, adult support, and access to opportunity.

Those experiences left me with a question I wanted to investigate using data: **how different are children’s circumstances and outcomes across the family and care arrangements in which they live?**

I did not want to assume that foster care or any other family structure automatically determines a child’s future. I wanted to compare children living with both parents, a mother only, a father only, or neither biological parent, while also examining the household conditions surrounding them.

My observations are the motivation for this project, not its statistical conclusion. Children in foster care do not share one experience, and this analysis does not claim that foster care causes school dropout, substance use, or any other outcome. The current dataset also does not contain a complete identifier for fostered children or a suitable child substance-use measure. These limits are stated throughout the project.

## Research question

How are children’s parent co-residence, household resources, geographic context, food security, and access to social protection associated with education and wellbeing outcomes in South Africa?

## What the project compares

The analysis uses four observable parent co-residence groups:

1. Lives with both biological parents
2. Lives with mother only
3. Lives with father only
4. Lives with neither biological parent

These are living-arrangement categories, not rankings of family quality. In particular, **living with neither biological parent is not the same as being formally fostered**. A child in this group may live with grandparents, other relatives, or another caregiver.

The comparison therefore focuses on measurable conditions around children:

* School attendance and grade repetition
* Household food insufficiency
* Household income and size
* Rural, farm, and provincial context
* Computer and fixed-internet access
* Child Support Grant and Foster Child Grant receipt
* Other selected indicators of services and opportunity

## Data source

The project uses the [Statistics South Africa General Household Survey 2025](https://www.datafirst.uct.ac.za/dataportal/index.php/catalog/1144), a nationally representative survey covering education, health, social development, housing, services, food security, and household resources.

The analysis contains 22608 sampled children aged 0–17, representing approximately 21.06 million children after applying the person survey weight.

The derived living-arrangement distribution reproduces Statistics South Africa’s published benchmark:

|Living arrangement|This analysis|Stats SA benchmark|
|-|-:|-:|
|Both parents|31.37%|31.4%|
|Mother only|45.92%|45.9%|
|Father only|4.20%|4.2%|
|Neither parent|18.52%|18.5%|

## Main findings so far

### Household conditions differ sharply

Children living with neither parent had the lowest median monthly household income per person, the lowest fixed-internet access, and the highest rural or farm residence rate. Mother-only households also had substantially fewer material resources than both-parent households.

|Living arrangement|Median monthly income per person|Child food insufficiency|Fixed internet|
|-|-:|-:|-:|
|Both parents|R2277|12.1%|32.5%|
|Mother only|R925|23.3%|13.2%|
|Father only|R1552|22.2%|21.7%|
|Neither parent|R875|23.8%|8.8%|

### School attendance is high across all groups

After adjusting for age, sex, province, geography, household income per person, household size, and food insufficiency, estimated school attendance was almost identical for children living with both parents, a mother only, or a father only.

|Living arrangement|Observed attendance|Adjusted attendance|
|-|-:|-:|
|Both parents|97.52%|97.17%|
|Mother only|96.99%|97.13%|
|Father only|97.38%|97.26%|
|Neither parent|95.47%|95.82%|

The result suggests that observed household and geographic conditions explain an important part of the difference between the both-parent and mother-only groups. Children living with neither parent still had a somewhat lower adjusted attendance estimate.

### Grade-repetition differences narrow after adjustment

The estimated repetition rate for the neither-parent group declined from 6.61% observed to 5.89% after adjustment. This reduces—but does not eliminate the descriptive difference.

These estimates describe associations. They do not establish that a living arrangement causes an education outcome.

## Responsible interpretation

This project is designed to understand conditions and support needs, not to judge children or rank families.

* Association does not prove causation.
* Parent co-residence is not a measure of care quality, safety, love, or caregiver commitment.
* The GHS does not directly identify all fostered or adopted children.
* Foster Child Grant receipt is not a complete foster-care classification.
* The survey excludes children living in institutions such as children’s homes.
* The current analysis does not test child substance use.
* Some groups especially the father only group have smaller samples and wider confidence intervals.
* Observed education estimates include survey-design-aware 95% confidence intervals; adjusted estimates currently remain point estimates.

The practical focus is therefore on conditions that can be improved: stable support, food security, educational assistance, connectivity, household resources, and access to social protection.

## Project structure

```text
data/raw/          Locally downloaded GHS files; not committed
data/processed/    Analysis-ready data; not committed
data/reference/    Source, variable, and validation trackers
docs/              Project scope, findings, and methodology
notebooks/         Step-by-step analysis notebooks
src/               Reusable Python analysis scripts
outputs/figures/   Publication-ready charts
outputs/tables/    Reproducible result tables
```

## Project outputs

* [Interactive dashboard](https://childhood-care-sa.singo-blessing10.chatgpt.site)
* [Initial weighted findings](docs/initial_findings.md)
* [Adjusted education findings](docs/adjusted_findings.md)
* [Methodology and limitations](docs/methodology.md)
* [Dashboard and presentation guide](docs/dashboard_and_presentation.md)
* [Portfolio presentation](outputs/Childhood-Care-Stability-Opportunity-SA-Presentation.pptx)

## Current status

* \[x] Personal motivation and ethical framing documented
* \[x] GHS 2025 person and household files processed
* \[x] Weighted living-arrangement distribution validated
* \[x] Education, food-security, and social-protection comparisons completed
* \[x] Household-context profiles completed
* \[x] Adjusted education point estimates completed
* \[x] Design-aware confidence intervals completed for observed education estimates
* \[x] Interactive dashboard published
* \[x] Portfolio presentation completed
* \[ ] Formal design-based inference for adjusted model contrasts
* \[ ] Additional analysis of early-childhood care indicators

## Data citation

Statistics South Africa. *General Household Survey 2025* \[dataset], Version 1. Pretoria: Statistics South Africa \[producer], 2026. Cape Town: DataFirst \[distributor], 2026. [DOI: 10.25828/a4a6-p161](https://doi.org/10.25828/a4a6-p161).


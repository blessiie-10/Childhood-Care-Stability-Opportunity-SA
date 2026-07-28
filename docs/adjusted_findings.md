# Adjusted Education Findings

## What this stage adds

This stage asks whether the descriptive education differences remain after children are compared on a common distribution of observed circumstances. It uses survey-weighted logistic regression and standardised predicted probabilities for school attendance and grade repetition.

The models adjust for age, age squared, sex, province, settlement type, monthly household income per person, household size and child food insufficiency. The observed estimates now include design-aware 95% confidence intervals; adjusted values remain point estimates. Formal tests of adjusted contrasts require a further design-based modelling stage.

|Outcome|Living arrangement|Observed estimate|Design-aware 95% CI|
|-|-|-:|-:|
|School attendance|Both parents|97.52%|96.93%-98.00%|
||Mother only|96.99%|96.49%-97.42%|
||Father only|97.38%|95.96%-98.31%|
||Neither parent|95.47%|94.62%-96.19%|
|Grade repetition|Both parents|4.29%|3.62%-5.09%|
||Mother only|5.26%|4.72%-5.85%|
||Father only|5.06%|3.60%-7.08%|
||Neither parent|6.61%|5.77%-7.55%|

## Unequal household contexts

The living-arrangement groups differ markedly in their observed household circumstances.

|Living arrangement|Sampled children|Rural or farm area|Median monthly income per person|Child food insufficiency|Computer access|Fixed internet|
|-|-:|-:|-:|-:|-:|-:|
|Both parents|5635|26.0%|R2,277|12.1%|37.8%|32.5%|
|Mother only|10586|47.3%|R925|23.3%|16.3%|13.2%|
|Father only|887|37.4%|R1,552|22.2%|26.4%|21.7%|
|Neither parent|5500|58.6%|R875|23.8%|13.6%|8.8%|

Children living with neither parent were the most likely to live in rural or farm areas and had the lowest median income per person and fixed-internet access. Mother-only households also had substantially fewer material resources than both-parent households. These patterns show why unadjusted comparisons should not be read as effects of family structure.

## Observed and adjusted education indicators

|Outcome|Living arrangement|Observed|Adjusted|
|-|-|-:|-:|
|School attendance, ages 5–17|Both parents|97.52%|97.17%|
||Mother only|96.99%|97.13%|
||Father only|97.38%|97.26%|
||Neither parent|95.47%|95.82%|
|Grade repetition, applicable learners|Both parents|4.29%|4.89%|
||Mother only|5.26%|5.20%|
||Father only|5.06%|4.60%|
||Neither parent|6.61%|5.89%|

After adjustment, school attendance is almost identical for the both-parent, mother-only and father-only groups: 97.17%, 97.13% and 97.26%, respectively. The unadjusted difference between the both-parent and mother-only groups is therefore largely accounted for by the observed demographic, geographic and household-resource variables in this model.

The adjusted attendance estimate for children living with neither parent rises from 95.47% to 95.82%. It remains about 1.35 percentage points below the both-parent adjusted estimate. Grade repetition for the neither-parent group falls from 6.61% observed to 5.89% adjusted, reducing but not eliminating the descriptive difference.

## Responsible interpretation

The results suggest that household resources and geography explain an important share of the observed education gaps. They do not show that living arrangements cause the remaining differences. Parent co-residence is an incomplete proxy for children's care: the data do not measure relationship quality, caregiver continuity, bereavement, migration histories or many school-level conditions.

The father-only group is comparatively small, so its estimate deserves particular caution. The current model also treats the published person weight as an analytic weight but does not yet use the full stratification and clustering information needed for design-based standard errors.

The practical conclusion is that living arrangement should be interpreted alongside material conditions. The results point toward resource access, food security, connectivity and educational support as more useful policy levers than ranking family types.

## Reproducibility

Run the adjusted stage after building the processed child file:

```bash
python src/adjusted\_analysis.py
```

The script writes the context-profile table, adjusted estimates, model diagnostics, and chart to `outputs/`.

## Source

Statistics South Africa. *General Household Survey 2025* \[dataset], Version 1. Pretoria: Statistics South Africa \[producer], 2026. Cape Town: DataFirst \[distributor], 2026. [DOI: 10.25828/a4a6-p161](https://doi.org/10.25828/a4a6-p161).


# Methodology

## 1\. Data source

The main source is the Statistics South Africa General Household Survey 2025, Version 1. The survey uses a two-stage stratified sample and provides person and household weights. It covers private households in all nine provinces and residents of worker's hostels, but excludes institutional living quarters such as children's homes, hospitals, prisons and military barracks.

This exclusion is important: the analysis represents children in the survey universe and cannot describe all children in residential or institutional care.

## 2\. Analysis population

* Main child sample: ages 0 to 17
* School-attendance analysis: initially ages 5 to 17, then refined using compulsory-schooling conventions and questionnaire applicability
* ECD analysis: ages covered by the GHS ECD questions
* All estimates use the person weight when reporting child-level results

## 3\. Living-arrangement derivation

The GHS variables `hhc\_moth\_parthh` and `hhc\_fath\_parthh` use `1 = Yes`, `2 = No`, and `8 = Not applicable`. For children whose parent is deceased, co-residence is coded `8`. To reproduce Stats SA's published living-arrangement measure, code `8` as parent not resident for this derivation.

|Mother present|Father present|Derived group|
|-|-|-|
|Yes|Yes|Both parents|
|Yes|No or not applicable|Mother only|
|No or not applicable|Yes|Father only|
|No or not applicable|No or not applicable|Neither parent|

True missing values remain available for audit and are excluded from comparisons that require a valid group.

## 4\. Outcomes and explanatory factors

### Primary outcomes

* School attendance: `edu\_attend`
* Grade repetition: `edu\_same`
* ECD attendance/type: `ecd\_chldatt`
* Health status: `hlt\_genhealth`
* Social grants: `soc\_grant\_csg`, `soc\_grant\_csg\_topup`, `soc\_grant\_car`, `soc\_grant\_fos`

### Household context

* Child food insufficiency: `fsd\_hung\_child` (`Never` versus any of `Seldom`, `Sometimes`, `Often`, or `Always`)
* Wider food-access indicators: `fsd\_worried`, `fsd\_healthy`, `fsd\_fewfoods`, `fsd\_skipped`, `fsd\_ateless`, `fsd\_ranout`, `fsd\_hungry`, `fsd\_whlday`
* Household income: `totmhinc`
* Household size: `hholdsz`
* Geography: `prov`, `geotype`, `metro`
* Services and opportunity: electricity, water, sanitation, internet, computer access, and health-facility travel time

### Early-care indicators

* Main caregiver relationship: `ECD\_CARE\_RELATION`
* Learning activities: `ecd\_read`, `ecd\_sing`, `ecd\_colour`, `ecd\_object`, `ecd\_count`, `ecd\_play`
* Discipline practices: `ECD\_DISCIPLINE\_DISTRACT`, `ECD\_DISCIPLINE\_EXPLAIN`, `ECD\_DISCIPLINE\_SHOUT`, `ECD\_DISCIPLINE\_SLAP`, `ECD\_DISCIPLINE\_ISOLATE`, `ECD\_DISCIPLINE\_NOTHING`

## 5\. Analysis sequence

1. Audit file formats, shapes, columns, value labels, missingness and duplicate keys.
2. Merge person and household files using the household identifier `uqnr` after validating uniqueness.
3. Filter children aged 0 to 17 and derive the four living-arrangement groups.
4. Reproduce Stats SA's national weighted distribution: both parents 31.4%, mother only 45.9%, father only 4.2%, neither parent 18.5%.
5. Produce weighted descriptive tables by group, age, sex, province and geography.
6. Compare outcome rates with 95% confidence intervals calculated by Taylor linearisation using the supplied survey strata, primary sampling units and person weights. Use a centred conservative adjustment for strata represented by a single PSU in an analysis sample.
7. Fit weighted logistic models after descriptive checks and use standardised predicted probabilities for attendance and grade repetition. The first adjusted results are point estimates confidence intervals and formal inference require a later design-based variance stage.
8. Test whether household resources explain part of the unadjusted differences.
9. Write conclusions about conditions and support needs, not about the inherent value of family types.

## 6\. Limitations

* The GHS is cross-sectional; it cannot establish cause and effect or measure long-term trajectories.
* Parent co-residence is not the same as care quality, emotional security or caregiver stability over time.
* The data do not directly identify adopted children.
* Foster-care grant receipt is not equivalent to a complete foster-care population.
* Some children living with neither parent may be safely cared for by grandparents or other relatives.
* Institutionalised children are outside the survey universe.
* Self-reported and proxy-reported answers can contain measurement error.
* Small subgroups may have unstable estimates, especially the father-only group or provincial cross-tabulations.
* The observed-rate intervals account for stratification and PSU clustering. The first adjusted probabilities remain point estimates model-contrast inference needs a further design-based modelling stage.


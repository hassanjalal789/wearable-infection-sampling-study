# Research summary

*Hassan Jalal · initial version, 17 September 2026 · drafted with AI assistance ([contributions](CONTRIBUTIONS.md))*

This summary describes a study I designed and conducted, written for readers without statistical training. The study is complete; I am publishing its supporting files in stages.

## The question

Resting heart rate often rises in the days before an infection causes symptoms, and smartwatch studies have used this to raise early alerts ([Mishra et al., 2020](https://doi.org/10.1038/s41551-020-00640-6); [Alavi et al., 2022](https://doi.org/10.1038/s41591-021-01593-2)). A low-power wearable cannot measure all the time, so it would take short measurements. If a device can measure for only a small part of each day, does the timing of those measurements affect how early an infection can be flagged?

Night-time measurements might be cleaner, because they are less disturbed by exercise, meals, and posture. In my main comparison I asked whether concentrating measurements in a fixed night-time window gives better early warning than spreading the same amount evenly across the day.

## The data

I collected no new data. I reused two public datasets from Stanford research teams (Phase 1 and Phase 2) containing heart-rate and step records from consumer wearables, with information about infections and symptom onset ([Mishra et al., 2020](https://doi.org/10.1038/s41551-020-00640-6); [Alavi et al., 2022](https://doi.org/10.1038/s41591-021-01593-2)).

After I applied the study's eligibility rules, the cohort contained 38 participants: 10 from Phase 1 and 28 from Phase 2. A comparison between two schedules was made for a participant only when both schedules left enough usable data to set that person's alert threshold. That was true for 30 of the 38 participants in every main comparison, so the main results are based on 30 people.

## The design

The study replayed the recorded data as if a wearable had followed different schedules:

- **S1, continuous:** all available readings, used as a reference.
- **S2, evenly spaced:** seven ten-minute bursts spread across the day, starting at midnight.
- **S3, night-time:** seven ten-minute bursts, one per hour from 00:00 to 06:59.
- **S4, rest-triggered:** a burst starts after five minutes without steps.
- **S5, random:** seven bursts at reproducible random times.
- **S3r and S6:** analysis-only schedules that pick rest periods using the whole day's step record, which a real device could not know in advance.

The sparse schedules were matched on a modelled energy budget: about 5% of the energy that continuous sampling would use in the energy model, which works out to seven ten-minute bursts. These energy figures come from a model with stated assumptions, not from measuring a real device.

The same detection method was used for every schedule. It compares heart rate with the person's usual heart rate at the same time of day and alerts when the difference stays unusually high for two days. Each threshold was tuned on earlier data so that alerts would occur on no more than about two days per month. The question was then whether an alert appeared in the 21 days before symptoms began, and how many days early it came.

Two schedules were compared person by person. A schedule "won" for a person if it alerted and the other did not, or if both alerted and it alerted earlier. The main summary number, θ, is the share of wins plus half the ties. A θ of 0.5 means the two schedules did equally well.

## The main result

The main comparison was night-time sampling (S3) against evenly spaced sampling (S2). Night-time sampling won for 8 people, lost for 12, and tied for 10, giving θ = 0.433, with a 95% confidence interval from 0.300 to 0.583 and p = 0.5034. Night-time sampling alerted before symptoms for 19 of the 30 people and evenly spaced sampling for 20.

**In plain terms: the study found no evidence that night-time sampling gives earlier warning than evenly spaced sampling.** Because this first test was not significant, the study's rules stopped formal testing, and the other comparisons are descriptive only.

## What it means

Within this dataset, energy model, and detection method, choosing a night-time window did not improve retrospective early warning. This does not show that timing can never matter. It shows that this particular timing strategy, tested this way, did not demonstrate an advantage.

The results also raise a question for future work. Continuous sampling alerted for 19 of the same 30 people, no more than the sparse schedules, and the typical warning of about two weeks is longer than the few days reported by the source dataset studies. I did not include a check of how often alerts would occur by chance, so it cannot show how much of the alerting reflects infection rather than normal day-to-day variation.

## Limitations

- The sample is small (30 people), so the results are uncertain.
- The data are retrospective, and the energy budgets are modelled rather than measured.
- The night-time window is a fixed clock time, not each person's actual sleep, and 3 of the 7 evenly spaced bursts also fall at night.
- The protocol documents were kept locally rather than registered publicly, some remain marked as drafts, and the sensitivity-analysis details were fixed after the main result was known.
- Attempts to reproduce earlier algorithms gave mixed results, and it is unknown whether some people appear in both datasets.

More detail is in [Results and limitations](RESULTS_AND_LIMITATIONS.md).

## Role

I formed the research question after discussing the general idea with an IT teacher, directed the protocol, its amendments, and the analysis workflow, ran or directed the analyses, interpreted the results, and wrote up the findings. AI tools assisted with drafting, editing, coding, debugging, and organising materials under my direction. See the [contribution statement](CONTRIBUTIONS.md) for details.

# Canonical D01/D02 targeted repair qualification v0.1

- SOURCE_FAILURE_EVIDENCE_COMMIT: `a9e306550c5dc47695e4c27c1812de4c3cad5641`
- TARGET_PARTITION_COUNT: `116`
- RESULT: `BLOCKED`
- BLOCKER: `TQSDK_EXISTING_AUTH_NOT_AVAILABLE`
- TARGETED_REACQUISITION_ATTEMPTED: `False`

## Deterministic diagnostic summary

- failures_by_product: `{"ag": 14, "al": 22, "au": 19, "cu": 21, "ni": 23, "rb": 17}`
- failures_by_contract: `{"SHFE.ag2501": 1, "SHFE.ag2503": 1, "SHFE.ag2507": 1, "SHFE.ag2508": 1, "SHFE.ag2509": 1, "SHFE.ag2510": 1, "SHFE.ag2511": 1, "SHFE.ag2601": 1, "SHFE.ag2602": 1, "SHFE.ag2603": 1, "SHFE.ag2606": 1, "SHFE.ag2607": 1, "SHFE.ag2608": 1, "SHFE.ag2609": 1, "SHFE.al2501": 1, "SHFE.al2502": 1, "SHFE.al2504": 1, "SHFE.al2505": 1, "SHFE.al2506": 1, "SHFE.al2508": 1, "SHFE.al2509": 1, "SHFE.al2510": 1, "SHFE.al2511": 1, "SHFE.al2512": 1, "SHFE.al2601": 1, "SHFE.al2602": 1, "SHFE.al2603": 1, "SHFE.al2604": 1, "SHFE.al2605": 1, "SHFE.al2606": 1, "SHFE.al2607": 1, "SHFE.al2608": 1, "SHFE.al2609": 1, "SHFE.al2610": 1, "SHFE.al2611": 1, "SHFE.al2612": 1, "SHFE.au2405": 1, "SHFE.au2409": 1, "SHFE.au2411": 1, "SHFE.au2501": 1, "SHFE.au2502": 1, "SHFE.au2503": 1, "SHFE.au2504": 1, "SHFE.au2507": 1, "SHFE.au2508": 1, "SHFE.au2509": 1, "SHFE.au2510": 1, "SHFE.au2511": 1, "SHFE.au2512": 1, "SHFE.au2602": 1, "SHFE.au2603": 1, "SHFE.au2604": 1, "SHFE.au2606": 1, "SHFE.au2608": 1, "SHFE.au2610": 1, "SHFE.cu2501": 1, "SHFE.cu2502": 1, "SHFE.cu2503": 1, "SHFE.cu2504": 1, "SHFE.cu2505": 1, "SHFE.cu2506": 1, "SHFE.cu2507": 1, "SHFE.cu2508": 1, "SHFE.cu2509": 1, "SHFE.cu2510": 1, "SHFE.cu2512": 1, "SHFE.cu2601": 1, "SHFE.cu2602": 1, "SHFE.cu2603": 1, "SHFE.cu2604": 1, "SHFE.cu2606": 1, "SHFE.cu2607": 1, "SHFE.cu2608": 1, "SHFE.cu2609": 1, "SHFE.cu2611": 1, "SHFE.cu2612": 1, "SHFE.ni2501": 1, "SHFE.ni2502": 1, "SHFE.ni2503": 1, "SHFE.ni2504": 1, "SHFE.ni2505": 1, "SHFE.ni2506": 1, "SHFE.ni2508": 1, "SHFE.ni2509": 1, "SHFE.ni2510": 1, "SHFE.ni2511": 1, "SHFE.ni2512": 1, "SHFE.ni2601": 1, "SHFE.ni2602": 1, "SHFE.ni2603": 1, "SHFE.ni2604": 1, "SHFE.ni2605": 1, "SHFE.ni2606": 1, "SHFE.ni2607": 1, "SHFE.ni2608": 1, "SHFE.ni2609": 1, "SHFE.ni2610": 1, "SHFE.ni2611": 1, "SHFE.ni2612": 1, "SHFE.rb2502": 1, "SHFE.rb2504": 1, "SHFE.rb2507": 1, "SHFE.rb2508": 1, "SHFE.rb2509": 1, "SHFE.rb2511": 1, "SHFE.rb2512": 1, "SHFE.rb2602": 1, "SHFE.rb2603": 1, "SHFE.rb2604": 1, "SHFE.rb2605": 1, "SHFE.rb2606": 1, "SHFE.rb2607": 1, "SHFE.rb2608": 1, "SHFE.rb2609": 1, "SHFE.rb2611": 1, "SHFE.rb2612": 1}`
- failures_by_month: `{"2024-01": 5, "2024-02": 5, "2024-03": 4, "2024-04": 4, "2024-05": 3, "2024-06": 4, "2024-07": 4, "2024-08": 6, "2024-09": 6, "2024-10": 5, "2024-11": 5, "2024-12": 5, "2025-01": 5, "2025-02": 5, "2025-03": 6, "2025-04": 5, "2025-05": 4, "2025-06": 6, "2025-07": 6, "2025-08": 6, "2025-09": 6, "2025-10": 2, "2025-11": 4, "2025-12": 5}`
- failure_shape_counts: `{"START_ONLY": 116}`
- missing_region_shape_counts: `{"MULTIPLE_REGIONS": 29, "PREFIX_ONLY": 87}`
- session_class_counts: `{"BOTH_DAY_AND_NIGHT": 116}`
- missing_session_class_counts: `{"BOTH_DAY_AND_NIGHT": 29, "NIGHT_ONLY": 87}`

The JSON companion records all 116 exact targets, request/return boundaries, current authority windows, missing regions, listing coverage, and the no-download blocking decision. No accepted artifact was modified.

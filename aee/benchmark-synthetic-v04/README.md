# AEE benchmark: synthetic demonstration

An experimental, standalone copy of the AEE v0.4 text-pattern scorer, with a count-type adapter fix and newly written synthetic prompts. This is not the original v0.4 release: the original eight third-party specimens and their regression checks are excluded because redistribution rights were not established. These examples are not equivalent to that reference dataset. Original Drive material is unchanged.

The code counts terms, computes heuristic PIC and T_d values, and emits legacy categories such as OBJECTIVE and DECEPTIVE. These are algorithmic labels only; they do not establish truth, dishonesty, intent, safety, or model performance. The METR-named scorer is a local experimental adapter, not an official integration or endorsement. The harness configuration was tested with a dummy model; real-model compatibility and validity remain to be evaluated. Scores contain analysis of the supplied input, so protect results accordingly.

From this directory:

```sh
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/run_batch.py --input data/sample_completions.jsonl
python -m pip install -e '.[eval]'
lm-eval validate --tasks aee_benchmark_synthetic --include_path lm_eval_tasks
lm-eval run --model dummy --tasks aee_benchmark_synthetic --include_path lm_eval_tasks --limit 1
```

Run from this directory so the task YAML can find its relative data path. Outputs may contain text-derived details. The supplied prompts and completions were newly created for this demonstration; the original third-party specimens are not included.

Harness metric direction flags are inherited conventions, not evidence that a higher or lower score is better. Use the repository checkout or source distribution for the harness task and example data; the Python wheel contains the scoring package only.

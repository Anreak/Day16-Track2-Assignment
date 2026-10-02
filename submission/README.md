# Azure CPU LightGBM submission

Deliverables from `README_other_clouds.md`, section A.Phần 6:

1. Benchmark terminal screenshot: `screenshots/output_terminal.png`.
2. Benchmark results: `benchmark_result.json` (matches the terminal screenshot).
3. Resource usage screenshot after the benchmark: `screenshots/resource_usage.png`.
4. Azure Cost Management screenshot: `screenshots/Azure Cost Management.png` (scope `ai-lab-rg`; no cost reported at capture time).
5. Cloud-init used: `infra/cloud-init-cpu.yaml`.
6. Eight-line report: `report.md`.

Supporting files: exact VM source `benchmark.py`, output log `benchmark_run.txt`, command explanations `commands_and_walkthrough.md`, resource observations `evidence/vm_resources.txt`, and cleanup confirmation `evidence/cleanup.json`.

Actual deployment: Azure for Students, East Asia, Standard_B2als_v2 (2 vCPU / 4 GB RAM), Ubuntu 22.04. This size was substituted for Standard_B2s because of capacity restrictions. The report describes the change and the dataset download fallback.

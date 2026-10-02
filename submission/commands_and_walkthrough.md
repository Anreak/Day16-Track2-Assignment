# Azure CPU lab walkthrough

## What I used

- Cloud: Microsoft Azure, Azure for Students subscription
- Region for deployed resources: East Asia (`eastasia`)
- Resource group: `ai-lab-rg` (created earlier in East US; the subscription allows deployment resources only in its approved regions)
- VM: `Standard_B2als_v2`, Ubuntu 22.04, 2 vCPUs and 4 GB RAM
- Network: VNet `ai-lab-vnet`, subnet `ai-lab-subnet`, NSG `ai-lab-nsg`
- SSH access: restricted to the user's current public IP as a `/32` CIDR
- Dataset: Kaggle Credit Card Fraud Detection (`mlg-ulb/creditcardfraud`), 284,807 rows
- Model: LightGBM binary classifier, 500 estimators, balanced class weights, 80/20 stratified train/test split, seed 42

The README's `Standard_B2s` was unavailable because of Azure capacity restrictions in every region allowed by this subscription. Azure validation accepted `Standard_B2als_v2` in East Asia. It has the same vCPU and RAM amounts as the requested VM. The report should identify the actual region and VM size used.

## Commands and what they do

### Select/check the Azure subscription

```powershell
az account show
az account set --subscription "Azure for Students"
```

`az account show` identifies the active account and subscription. `az account set` selects the subscription for later CLI commands.

### Create a resource group

```powershell
az group create --name ai-lab-rg --location eastus
```

A resource group is a management container for the lab resources. Azure policy allowed creating this group, but required the actual VNet, NSG, public IP, and VM to use an approved deployment region.

### Create the VNet and subnet in East Asia

```powershell
az network vnet create `
  --resource-group ai-lab-rg --name ai-lab-vnet --location eastasia `
  --address-prefixes 10.20.0.0/16 `
  --subnet-name ai-lab-subnet --subnet-prefixes 10.20.1.0/24
```

The VNet is the VM's private network. The subnet is a smaller address range inside that VNet.

### Create an NSG and allow SSH only from my current IP

```powershell
az network nsg create --resource-group ai-lab-rg --name ai-lab-nsg --location eastasia
az network nsg rule create `
  --resource-group ai-lab-rg --nsg-name ai-lab-nsg `
  --name allow-ssh-from-me --priority 100 `
  --source-address-prefixes <MY_PUBLIC_IP>/32 `
  --destination-port-ranges 22 --access Allow --protocol Tcp
```

The NSG is a network firewall. Port 22 is SSH. `/32` means exactly one IPv4 address, so SSH is not open to the whole internet. Replace the placeholder only if recreating the lab; the user's IP may change.

### Create the Ubuntu CPU VM

```powershell
az vm create `
  --resource-group ai-lab-rg --name ai-cpu-node --location eastasia `
  --image Ubuntu2204 --size Standard_B2als_v2 `
  --admin-username azureuser `
  --vnet-name ai-lab-vnet --subnet ai-lab-subnet --nsg ai-lab-nsg `
  --generate-ssh-keys --custom-data cloud-init-cpu.yaml
```

This provisions the Linux machine and connects it to the lab network. `--generate-ssh-keys` creates or uses a local SSH key pair; the private key must stay private. `--custom-data` passes the cloud-init file, which installs Python, pip, LightGBM, scikit-learn, pandas, NumPy, and Kaggle CLI during first boot.

### Download the dataset and run the benchmark on the VM

```bash
KAGGLE_CONFIG_DIR=/home/azureuser/.kaggle \
  kaggle datasets download -d mlg-ulb/creditcardfraud \
  --unzip -p /home/azureuser/ml-benchmark

cd /home/azureuser/ml-benchmark
HOME=/home/azureuser python3 benchmark.py
```

The first command downloads and extracts the Kaggle dataset. The credentials file was transferred over SSH with owner-only permissions and removed from the VM after the download. The second command runs the script and writes `benchmark_result.json` in the working directory.

### Check VM memory and network counters

```bash
free -h
ip -s link
```

`free -h` reports RAM and swap in readable units. `ip -s link` reports interface packet and byte counters.

### Clean up after retrieving deliverables

```powershell
az group delete --name ai-lab-rg
az group exists --name ai-lab-rg
```

Deleting the resource group removes the lab VM, disk, public IP, NSG, and VNet. The second command should return `false` after deletion completes. Do this only after confirming all deliverables are downloaded.

## Measured benchmark results

- Data rows / features: 284,807 / 30
- Data load: 1.221 seconds
- Training: 12.934 seconds
- Estimators used: 500 (the script did not use early stopping)
- AUC-ROC: 0.9451
- Accuracy: 0.99954
- F1: 0.86170
- Precision: 0.90000
- Recall: 0.82653
- One-row inference latency: 1.499 ms
- 1,000-row inference throughput: 42,381.39 rows/second

The accuracy is high partly because fraud is rare in this dataset; AUC, precision, recall, and F1 are useful complementary measures. The train/test split was stratified and reproducible with random seed 42.

## Resource and billing notes

At the post-run sample on 2026-10-02 at 21:40:19 (UTC+7), the VM reported 3.8 GiB total memory, 253 MiB used, 1.7 GiB free, and 3.3 GiB available. CPU was 93.8% idle. The eth0 cumulative counters were 410,883,247 RX bytes and 18,226,148 TX bytes. These are readings after training, not peak resource use during training.

The recreated VM initially lacked the CSV. The Kaggle CLI download returned HTTP 403, and the temporary credential file was removed from the VM. The dataset was restored from https://media.githubusercontent.com/media/sabin74/credit_card_fraud_detection/main/creditcard.csv, then checked for SHA-256 76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89, 284,807 rows, the expected 31 columns, and 492 fraud labels. The final screenshot, benchmark_result.json, and benchmark_run.txt all represent the user's rerun (training 12.934 seconds).

The Azure Portal showed $96.14 available credit before this run, with active Azure for Students credit expiring 2027-08-18. Cost Management may update with a delay; use a screenshot from the actual billing scope after the usage appears. This walkthrough does not claim a final post-lab balance.

Final cleanup was verified at 2026-10-02 21:48:52 (UTC+7). After `az group delete --name ai-lab-rg --yes --no-wait`, `az group exists --name ai-lab-rg -o tsv` returned `false`. The group contained only the lab VM, OS disk, NIC, public IP, NSG, and VNet. See `evidence/cleanup.json` for the verification record.

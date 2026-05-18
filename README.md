# Kubernetes Cluster on VMware vSphere — Datacenter Project

Production-like Kubernetes cluster deployed on real hardware in a datacenter with full DevOps stack: CI/CD, monitoring, secrets management, and GitOps.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VMware vSphere                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  k8s-master  │  │  k8s-worker  │  │   GitLab     │  │
│  │ 10.100.0.200 │  │ 10.100.0.210 │  │ 10.100.0.220 │  │
│  │              │  │              │  │              │  │
│  │ Control Plane│  │  Workloads   │  │ GitLab EE    │  │
│  │ ArgoCD       │  │  Pods        │  │ Runner       │  │
│  │ etcd         │  │              │  │ Docker       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Orchestration | Kubernetes v1.30 (kubeadm) | Container orchestration |
| Runtime | containerd v2.2.1 | Container runtime |
| CNI | Calico v3.27 | Pod networking |
| Package Manager | Helm v3 | Kubernetes package management |
| CI/CD | GitLab EE + GitLab Runner | Build and deploy pipelines |
| GitOps | ArgoCD | Automated deployments from Git |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| Ingress | Nginx Ingress Controller | Traffic routing |
| Secrets | HashiCorp Vault | Secret management with sidecar injection |
| Registry | Docker Hub | Container image storage |
| Storage | local-path-provisioner | PersistentVolumes |

## CI/CD Pipeline Flow

```
Developer pushes code to GitLab
    → GitLab Runner builds Docker image
    → Pushes image to Docker Hub
    → Deploys to Kubernetes via kubectl
    → Application updated automatically
```

## Vault Integration

Secrets are not hardcoded in manifests. HashiCorp Vault injects secrets into pods via sidecar:

```
Pod starts → Vault Agent sidecar authenticates via K8s SA
           → Fetches secrets from Vault
           → Writes to /vault/secrets/config
           → Application reads secrets from file
```

## Infrastructure Details

### Virtual Machines

| VM | Role | IP | CPU | RAM | Disk | OS |
|----|------|----|-----|-----|------|----|
| k8s-master | Control Plane | 10.100.0.200 | 2 | 4GB | 30GB | Ubuntu 24.04 LTS |
| k8s-worker | Worker Node | 10.100.0.210 | 2 | 4GB | 17GB | Ubuntu 24.04 LTS |
| gitlab | GitLab + Runner | 10.100.0.220 | 2 | 8GB | 30GB | Ubuntu 24.04 LTS |

### Kubernetes Namespaces

| Namespace | Components |
|-----------|-----------|
| default | test-app (Flask + Vault sidecar) |
| watchlist-dev | Watchlist app (FastAPI + PostgreSQL + Redis + Celery + Nginx) |
| argocd | ArgoCD server and controllers |
| monitoring | Prometheus + Grafana + Alertmanager |
| ingress-nginx | Nginx Ingress Controller |
| vault | HashiCorp Vault + Agent Injector |

### Access Points

| Service | URL |
|---------|-----|
| Test App | http://10.100.0.200:30090 |
| Watchlist | http://10.100.0.200:30080 |
| Grafana | http://10.100.0.200:30030 |
| Prometheus | http://10.100.0.200:30090 |
| ArgoCD | https://10.100.0.200:30088 |
| GitLab | http://10.100.0.220 |
| Ingress | http://10.100.0.200:30100 |
| Vault | http://10.100.0.200:30200 |

## Project Structure

```
datacenter-k8s/
├── README.md
├── docs/
│   ├── 01-vm-setup.md           # VM creation and OS setup
│   ├── 02-kubernetes-setup.md    # kubeadm cluster initialization
│   ├── 03-monitoring.md          # Prometheus + Grafana
│   ├── 04-ingress.md             # Nginx Ingress Controller
│   ├── 05-gitlab-cicd.md         # GitLab + Runner + Pipeline
│   └── 06-vault.md               # HashiCorp Vault
├── gitlab-ci/
│   └── .gitlab-ci.yml
├── k8s/
│   └── deployment.yaml
├── app/
│   ├── app.py
│   └── Dockerfile
└── vault/
    └── vault-policy.hcl
```

## Quick Reproduce

1. Create 3 VMs on VMware vSphere (Ubuntu 24.04)
2. Configure networking (static IPs, netplan)
3. Install containerd + kubeadm on master and worker
4. `kubeadm init` on master, `kubeadm join` on worker
5. Install Calico CNI
6. Install Helm, ArgoCD, Prometheus, Grafana, Ingress, Vault via Helm
7. Install GitLab EE + Runner on separate VM
8. Configure CI/CD pipeline
9. Deploy application

## Key Learnings

- **kubeadm** on real hardware vs k3s on cloud — production-grade cluster setup
- **GitLab self-hosted** — full control over CI/CD infrastructure
- **Vault sidecar injection** — zero secrets in Git, automatic rotation
- **Helm charts** — templated deployments across environments
- **ArgoCD GitOps** — cluster state always matches Git
- **Prometheus + Grafana** — real-time cluster monitoring

# Kubernetes Cluster on VMware vSphere — Datacenter Project

Production-grade Kubernetes cluster on real hardware in a datacenter with full DevOps stack: CI/CD, monitoring, logging, secrets management, auto-scaling, and GitOps.

## Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Orchestration | Kubernetes v1.30 (kubeadm) | Container orchestration |
| Runtime | containerd v2.2.1 | Container runtime |
| CNI | Calico | Pod networking + Network Policies |
| Package Manager | Helm v3 | Kubernetes package management |
| CI/CD | GitLab EE + Runner | Build and helm bump pipelines |
| GitOps | ArgoCD (App of Apps) | Automated deployments from Git |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| Logging | Loki + Promtail | Centralized log aggregation |
| Alerting | Alertmanager → Telegram | Real-time notifications |
| Ingress | Nginx Ingress Controller | Traffic routing |
| Secrets | HashiCorp Vault | Sidecar injection, zero secrets in Git |
| Auto-scaling | HPA + metrics-server | Scale pods under load |
| Security | Network Policies | Namespace isolation |
| Registry | Docker Hub | Container image storage |

## CI/CD Pipeline — Helm Bump

```
Developer pushes code to GitLab
  → Runner builds Docker image (tag: timestamp)
  → Pushes to Docker Hub
  → CI updates image tag in GitOps repo (helm bump)
  → ArgoCD detects Git change
  → ArgoCD deploys new version to cluster
  → CI never touches kubectl — only Git
```

## Infrastructure

| VM | Role | IP | RAM | Disk | OS |
|----|------|----|-----|------|----|
| k8s-master | Control Plane | 10.100.0.200 | 4GB | 30GB | Ubuntu 24.04 |
| k8s-worker | Worker Node | 10.100.0.210 | 8GB | 17GB | Ubuntu 24.04 |
| gitlab | GitLab + Runner | 10.100.0.220 | 8GB | 30GB | Ubuntu 24.04 |

## Namespaces

| Namespace | Components |
|-----------|-----------|
| default | test-app (Flask + Vault sidecar + HPA) |
| watchlist-dev | Watchlist (FastAPI + PostgreSQL + Redis + Celery + Nginx) |
| argocd | ArgoCD server and controllers |
| monitoring | Prometheus + Grafana + Alertmanager + Loki + Promtail |
| ingress-nginx | Nginx Ingress Controller |
| vault | HashiCorp Vault + Agent Injector |

## Key Features Demonstrated

**GitOps (App of Apps)**: One ArgoCD Application creates all others. Entire cluster reproducible from a single Git repo with one command.

**Helm Bump CI/CD**: GitLab CI builds and pushes images, then updates image tags in the GitOps repo. CI has no cluster access — ArgoCD handles all deployments.

**Vault Sidecar Injection**: Secrets injected into pods via sidecar container. Zero secrets stored in Git. Applications read secrets from files, not environment variables.

**Auto-Scaling**: HPA scales pods based on CPU utilization. Tested with simulated DDoS: 1 pod → 3 pods under load → back to 1 when load drops.

**Centralized Logging**: Promtail collects logs from all pods on all nodes, sends to Loki, queryable in Grafana with LogQL.

**Real-time Alerting**: Alertmanager sends alerts to Telegram bot when pods crash, nodes go down, or resources are overcommitted.

**Network Isolation**: Calico Network Policies restrict traffic between namespaces. Only explicitly allowed communication passes through.

## Repositories

| Repo | Purpose |
|------|---------|
| [datacenter-k8s](https://github.com/MassonTG/datacenter-k8s) | Documentation and configs (this repo) |
| [datacenter-gitops](https://github.com/MassonTG/datacenter-gitops) | App of Apps — full cluster from one repo |
| [bog-watchlist-app](https://github.com/bog-watchlist/bog-watchlist-app) | Watchlist source code + CI |
| [bog-watchlist-helm](https://github.com/bog-watchlist/bog-watchlist-helm) | Watchlist Helm charts (dev/prod values) |
| [bog-watchlist-argocd](https://github.com/bog-watchlist/bog-watchlist-argocd) | Watchlist ArgoCD Applications |

## Quick Reproduce

1. Create 3 Ubuntu 24.04 VMs on vSphere (or any hypervisor)
2. Install containerd + kubeadm, init cluster, join worker
3. Install Calico CNI, Helm
4. Install ArgoCD, apply datacenter-apps Application
5. ArgoCD deploys everything else automatically from Git
6. Install GitLab EE + Runner on separate VM
7. Full production cluster in ~30 minutes

## Documentation

- [VM Setup](docs/01-vm-setup.md)
- [Kubernetes Setup](docs/02-kubernetes-setup.md)
- [Monitoring](docs/03-monitoring.md)
- [Ingress](docs/04-ingress.md)
- [GitLab CI/CD](docs/05-gitlab-cicd.md)
- [Vault](docs/06-vault.md)

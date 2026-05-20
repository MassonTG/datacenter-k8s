# Datacenter GitOps — App of Apps

Full GitOps management of Kubernetes cluster via ArgoCD App of Apps pattern. One command recreates the entire cluster from Git.

## One Command to Rule Them All

```bash
kubectl apply -f datacenter-apps.yaml
```

ArgoCD automatically deploys everything:

| Application | Source | What it does |
|-------------|--------|-------------|
| prometheus | prometheus-community helm chart | Monitoring + Grafana dashboards |
| loki | grafana helm chart | Centralized log aggregation |
| promtail | grafana helm chart | Log collection from all nodes |
| ingress-nginx | kubernetes helm chart | Traffic routing |
| vault | hashicorp helm chart | Secret management via sidecar |
| test-app | this repo (k8s/test-app) | Flask app with Vault + HPA |
| watchlist-dev | bog-watchlist-helm repo | Microservice app |
| network-policies | this repo (k8s/network-policies) | Namespace isolation |

## CI/CD Flow — Helm Bump

```
Developer pushes code to GitLab (10.100.0.220)
  → GitLab Runner builds Docker image with timestamp tag
  → Pushes image to Docker Hub
  → CI clones this repo and updates image tag (helm bump)
  → CI pushes change to GitHub
  → ArgoCD detects change and deploys new version
  → CI has NO access to the cluster — only Git
```

## Alerting

Alertmanager sends real-time alerts to Telegram bot when issues occur in the cluster (pod crashes, node unreachable, CPU overcommit).

## Auto-Scaling (HPA)

HorizontalPodAutoscaler monitors CPU usage and scales pods automatically:

```
Normal load:  1 pod  (cpu: 8%)
Under attack: 3 pods (cpu: 100% → distributed to 37% each)
Load drops:   1 pod  (scales back down after 5 minutes)
```

## Network Policies

Calico-based network policies isolate namespaces:
- Pods in watchlist-dev can only talk to each other
- External traffic allowed only to frontend and test-app
- Prometheus can reach all namespaces for metrics collection

## Observability Stack

- **Metrics**: Prometheus collects, Grafana visualizes (port 30030)
- **Logs**: Promtail collects from all pods → Loki stores → Grafana queries
- **Alerts**: Alertmanager evaluates rules → Telegram bot notifications

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      VMware vSphere                          │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │  k8s-master    │  │  k8s-worker    │  │   GitLab       │ │
│  │  10.100.0.200  │  │  10.100.0.210  │  │  10.100.0.220  │ │
│  │  4GB RAM       │  │  8GB RAM       │  │  8GB RAM       │ │
│  │                │  │                │  │                │ │
│  │  Control Plane │  │  Workloads     │  │  GitLab EE     │ │
│  │  ArgoCD        │  │  Pods + HPA    │  │  Runner        │ │
│  │  etcd          │  │  Vault         │  │  Docker        │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Project Structure

```
datacenter-gitops/
├── apps/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── prometheus.yaml
│       ├── loki.yaml
│       ├── promtail.yaml         (new)
│       ├── ingress.yaml
│       ├── vault.yaml
│       ├── test-app.yaml
│       ├── watchlist.yaml
│       └── network-policies.yaml (new)
└── k8s/
    ├── test-app/
    │   └── deployment.yaml       (HPA + resources)
    └── network-policies/
        └── default-deny.yaml     (new)
```

## Related Repos

- [datacenter-k8s](https://github.com/MassonTG/datacenter-k8s) — cluster setup documentation
- [bog-watchlist-app](https://github.com/bog-watchlist/bog-watchlist-app) — Watchlist source code + CI
- [bog-watchlist-helm](https://github.com/bog-watchlist/bog-watchlist-helm) — Watchlist Helm charts
- [bog-watchlist-argocd](https://github.com/bog-watchlist/bog-watchlist-argocd) — Watchlist ArgoCD Applications

## Full Stack

Kubernetes v1.30 (kubeadm) · containerd v2.2.1 · Calico CNI · Helm v3 · ArgoCD (App of Apps) · GitLab EE + Runner · Prometheus · Grafana · Loki · Promtail · Alertmanager · Telegram Bot · Nginx Ingress · HashiCorp Vault · HPA · Network Policies · metrics-server · Docker Hub

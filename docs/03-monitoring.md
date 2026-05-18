# Monitoring — Prometheus + Grafana

## Install via Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.service.type=NodePort \
  --set grafana.service.nodePort=30030 \
  --set prometheus.prometheusSpec.service.type=NodePort \
  --set prometheus.prometheusSpec.service.nodePort=30090
```

## Access

- Grafana: http://10.100.0.200:30030 (admin / prom-operator)
- Prometheus: http://10.100.0.200:30090

## Dashboards

After connecting Prometheus as data source in Grafana, imported "Kubernetes / Compute Resources / Cluster" dashboard showing:

- CPU Utilisation: 24.2%
- Memory Usage: 47.3%
- Per-namespace breakdown (argocd, watchlist-dev, monitoring)

## Components

```bash
kubectl get pods -n monitoring
# alertmanager-xxx          2/2  Running
# prometheus-grafana-xxx    3/3  Running
# prometheus-operator-xxx   1/1  Running
# kube-state-metrics-xxx    1/1  Running
# prometheus-xxx            2/2  Running
# node-exporter-xxx         1/1  Running  (on each node)
```

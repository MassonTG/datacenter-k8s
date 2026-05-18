# Kubernetes Cluster Setup

## Initialize Control Plane (master only)

```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --apiserver-advertise-address=10.100.0.200
```

Configure kubectl:

```bash
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Install Calico CNI (master only)

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

## Join Worker Node

On worker, run the join command from kubeadm init output:

```bash
sudo kubeadm join 10.100.0.200:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash>
```

## Verify Cluster

```bash
kubectl get nodes
# NAME         STATUS   ROLES           AGE   VERSION
# k8s-master   Ready    control-plane   5m    v1.30.14
# k8s-worker   Ready    <none>          1m    v1.30.14
```

## Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"NodePort","ports":[{"port":443,"targetPort":8080,"nodePort":30088}]}}'
```

## Install local-path-provisioner (for PersistentVolumes)

```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.26/deploy/local-path-storage.yaml
kubectl patch storageclass local-path -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

## Deploy Watchlist via ArgoCD

Connected ArgoCD to GitHub repo `bog-watchlist-helm` and created Application pointing to Helm chart with dev values. ArgoCD automatically syncs cluster state with Git.

```bash
kubectl get pods -n watchlist-dev
# celery-xxx      1/1  Running
# fastapi-xxx     1/1  Running
# frontend-xxx    1/1  Running
# postgres-0      1/1  Running
# redis-xxx       1/1  Running
```

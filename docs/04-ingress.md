# Ingress Controller — Nginx

## Install via Helm

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30100 \
  --set controller.service.nodePorts.https=30443
```

## Verify

```bash
kubectl get pods -n ingress-nginx
# ingress-nginx-controller-xxx   1/1  Running

kubectl get svc -n ingress-nginx
# ingress-nginx-controller   NodePort   30100(HTTP), 30443(HTTPS)
```

## Usage

With a domain, Ingress resources route traffic by hostname:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: watchlist
  namespace: watchlist-dev
spec:
  ingressClassName: nginx
  rules:
    - host: watchlist.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

Note: Full Ingress rules require a domain name. In our datacenter environment with only internal IPs, services are accessed via NodePort.

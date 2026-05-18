# HashiCorp Vault — Secrets Management

## Install via Helm

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set server.dev.enabled=true \
  --set server.service.type=NodePort \
  --set server.service.nodePort=30200
```

## Configure Vault

```bash
kubectl exec -it vault-0 -n vault -- sh

# Create secrets
vault kv put secret/test-app \
  db_password="SuperSecret123" \
  api_key="my-api-key-12345"

# Enable Kubernetes auth
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

# Create policy
vault policy write test-app - <<EOF
path "secret/data/test-app" {
  capabilities = ["read"]
}
EOF

# Create role
vault write auth/kubernetes/role/test-app \
  bound_service_account_names=test-app \
  bound_service_account_namespaces=default \
  policies=test-app \
  ttl=1h
```

## Create ServiceAccount

```bash
kubectl create serviceaccount test-app -n default
```

## Deployment with Vault Sidecar

Vault Agent Injector automatically injects a sidecar container that fetches secrets:

```yaml
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "test-app"
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/test-app"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/test-app" -}}
          export DB_PASSWORD="{{ .Data.data.db_password }}"
          export API_KEY="{{ .Data.data.api_key }}"
          {{- end }}
    spec:
      serviceAccountName: test-app
```

## How It Works

```
1. Pod starts with serviceAccountName: test-app
2. Vault Agent Injector mutating webhook detects annotations
3. Injects init + sidecar container
4. Init container authenticates to Vault using K8s ServiceAccount token
5. Fetches secrets from secret/data/test-app
6. Writes secrets to /vault/secrets/config
7. Application reads secrets from file (not environment variables)
8. Sidecar keeps secrets refreshed
```

## Verify

```bash
kubectl get pods -n default
# test-app-xxx   2/2  Running   (2/2 = app + vault sidecar)

# Check secrets inside pod
kubectl exec test-app-xxx -c test-app -- cat /vault/secrets/config
# export DB_PASSWORD="SuperSecret123"
# export API_KEY="my-api-key-12345"
```

## Security Benefits

- Zero secrets in Git repositories
- Automatic secret rotation
- Audit log of secret access
- Fine-grained access control via policies
- Short-lived tokens (TTL-based)

# GitLab CI/CD

## Install GitLab EE

```bash
# On gitlab VM (10.100.0.220)
sudo apt-get update -y
sudo apt-get install -y curl openssh-server ca-certificates
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://10.100.0.220" apt-get install gitlab-ee
```

## Install GitLab Runner

```bash
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner -y
```

## Install Docker (for Runner)

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker gitlab-runner
```

## Register Runner

```bash
sudo gitlab-runner register \
  --url http://10.100.0.220 \
  --token <runner-token> \
  --executor docker \
  --docker-image docker:latest
```

### Runner Config (/etc/gitlab-runner/config.toml)

Key settings:

```toml
[[runners]]
  executor = "docker"
  run_untagged = true
  [runners.docker]
    privileged = true
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]
```

## Docker Insecure Registry (for GitLab Registry)

```json
# /etc/docker/daemon.json
{
  "insecure-registries": ["10.100.0.220:5050"]
}
```

## CI/CD Pipeline (.gitlab-ci.yml)

```yaml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker build -t $DOCKERHUB_USER/test-app:latest .
    - docker push $DOCKERHUB_USER/test-app:latest

deploy:
  stage: deploy
  image:
    name: bitnami/kubectl:latest
    entrypoint: ['']
  script:
    - export KUBECONFIG=$KUBECONFIG_CONTENT
    - kubectl apply -f k8s/
    - kubectl rollout restart deployment/test-app -n default
  only:
    - main
```

## CI/CD Variables

| Variable | Type | Purpose |
|----------|------|---------|
| KUBECONFIG_CONTENT | File | Kubernetes cluster access |
| DOCKERHUB_USER | Variable | Docker Hub username |
| DOCKERHUB_TOKEN | Variable | Docker Hub access token |

## Pipeline Flow

```
git push → GitLab detects .gitlab-ci.yml
         → Runner picks up job
         → Build: docker build + push to Docker Hub
         → Deploy: kubectl apply to k8s cluster
         → App updated on http://10.100.0.200:30090
```

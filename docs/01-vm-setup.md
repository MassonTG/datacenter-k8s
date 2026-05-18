# VM Setup on VMware vSphere

## Create VMs

Created 3 Ubuntu 24.04 Server VMs on VMware vSphere (ESXi hypervisor):

- k8s-master: 2 CPU, 4GB RAM, 30GB disk
- k8s-worker: 2 CPU, 4GB RAM, 17GB disk
- gitlab: 2 CPU, 8GB RAM, 30GB disk

## Network Configuration

Each VM configured with static IP via netplan:

```yaml
# /etc/netplan/50-cloud-init.yaml
network:
  version: 2
  ethernets:
    ens192:
      addresses:
        - 10.100.0.200/24    # master
        # - 10.100.0.210/24  # worker
        # - 10.100.0.220/24  # gitlab
      routes:
        - to: default
          via: 10.100.0.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply
```

## Base Setup (master + worker)

```bash
# Set hostname
sudo hostnamectl set-hostname k8s-master  # or k8s-worker

# Disable swap (required for Kubernetes)
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Load kernel modules
sudo tee /etc/modules-load.d/k8s.conf <<EOF
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# Configure sysctl
sudo tee /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system
```

## Install containerd (master + worker)

```bash
sudo apt-get update
sudo apt-get install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
```

## Install kubeadm (master + worker)

```bash
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

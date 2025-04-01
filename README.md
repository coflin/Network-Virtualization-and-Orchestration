# BGP SDN Setup - Automated Lab Walkthrough

This repository documents the automation and configuration of a BGP-enabled Software Defined Network (SDN) lab environment using OpenStack VMs, Docker containers, FRRouting (FRR), and GoBGP.

---

## 📦 Repository Structure

```
lab9/
├── configs/
│   ├── frr/
│   │   ├── daemons
│   │   └── frr.conf
│   └── gobgp/
│       └── gobgp.conf
├── configure_security.py
├── create_vms.py
├── create_vns.py
├── frr_setup.py
├── requirements.txt
├── sdn_bgp.py
├── test_connectivity.py
```

---

## ⚙️ Environment Setup

- **Platform**: OpenStack (DevStack)
- **OS**: Ubuntu Server 24.04 (headless)
- **Containers**: Docker
- **Languages**: Python 3.12

---

## 🔧 Automation Scripts

### 1. Virtual Networks & Routers
- `create_vns.py`
  - Automates creation of virtual networks (VN), subnets, and routers.
  - Connects them to the public network.

### 2. VMs
- `create_vms.py`
  - Automates spinning up VMs in single-tenant and multi-tenant modes.
  - Assigns floating IPs and ensures Internet access.

### 3. Security Configuration
- `configure_security.py`
  - Sets up security groups to allow all ICMP, TCP, and SSH traffic (ingress and egress).

### 4. FRR Setup (BGP Peer)
- `frr_setup.py`
  - Builds and runs a Docker container using `frrouting/frr:latest`.
  - Starts zebra and bgpd daemons.
  - Configures BGP using `vtysh`.
  - Sample:
    ```bash
    router bgp 65001
      bgp router-id 1.1.1.1
      neighbor 10.0.0.2 remote-as 65002
      network 10.0.0.0/24
    ```

### 5. GoBGP Setup (SDN Controller)
- `sdn_bgp.py`
  - Runs a GoBGP container with a mounted configuration file.
  - Peers with FRR.
  - Sample config (`gobgp.conf`):
    ```toml
    [global.config]
    as = 65002
    router-id = "10.0.0.2"

    [[neighbors]]
    [neighbors.config]
    neighbor-address = "10.0.0.1"
    peer-as = 65001
    ```

---

## ✅ Validation

- FRR confirms successful BGP peering:
  ```
  Neighbor        V         AS   MsgRcvd   MsgSent   Up/Down State/PfxRcd
  10.0.0.2        4      65002        14        14 00:06:17     (Policy)
  ```

- Connectivity tested between VMs.
- BGP sessions established, no advertisements exchanged (by design).

---

## 🔍 Troubleshooting

- Ensure no stale PID files in FRR: `rm -f /var/run/frr/*.pid`
- Make sure GoBGP config path is correct and permissions are valid.
- Restart containers if BGP sessions don’t establish automatically.

---

## 📝 Notes

- All components run inside Docker on the OpenStack hypervisor node.
- This setup is modular and can be extended to include route advertisement, ExaBGP, Ryu, etc.

---

## 📁 To-Do

- Automate testing with `test_connectivity.py`.
- Export network topology as visual diagrams.

---

## 📌 Author
Sneha Irukuvajjula




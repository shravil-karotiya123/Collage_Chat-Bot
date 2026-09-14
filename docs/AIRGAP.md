# MRPL AI Workbench — Air-Gap Sovereignty & Network Policies

## Network Policy Framework

The application maintains an independent network security and trust plane enforcing zero unauthorized egress.

---

## 1. Network Trust Profiles

| Profile | Target Environment | External HTTP | Local Ollama | Telemetry / Cloud |
|---|---|---|---|---|
| `STRICT_AIRGAP` | Production Refinery OT | **REJECTED** | `127.0.0.1:11434` strictly | **DISABLED** |
| `INDUSTRIAL_LAN` | On-Premises Refinery Plant LAN | Local Subnet Only | `127.0.0.1:11434` | **DISABLED** |
| `DEVELOPMENT` | Offline Local Development Workstation | Local Subnet / Mocks | `127.0.0.1:11434` | Mocked / Local |

---

## 2. Enforcement Components

- [`AirGapEnforcer`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/core/network/airgap_enforcer.py): Application-level network policy interceptor blocking non-loopback socket requests.
- [`AirGapSentinel`](file:///c:/Users/shrav/OneDrive/Desktop/MRPL_AI_Workbench/src/core/network/sentinel.py): Real-time socket binding auditor logging all connection attempts into the audit ledger.

---

## 3. Defense-in-Depth Recommendation

> **Security Notice**: Application-level network enforcement provides auditability and internal policy compliance. For production refinery deployment, it must be paired with host OS firewall rules (`iptables` / Windows Defender Firewall with Advanced Security) and physical network air-gapping.

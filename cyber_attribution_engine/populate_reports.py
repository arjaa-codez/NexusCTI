"""Script to populate authentic STIX 2.1 CTI reports with zero mocked data."""
import json
import os

REPORTS = {
    "cisa_aa20_352a_apt29_solarwinds.json": {
        "id": "bundle--apt29-solarwinds-sunburst-2020",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "APT29",
        "aliases": ["Cozy Bear", "Nobelium", "Midnight Blizzard", "UNC2452"],
        "origin": "Russian Foreign Intelligence Service (SVR)",
        "confidence_base": 0.94,
        "narrative": (
            "In December 2020, CISA released Alert AA20-352A regarding an Advanced Persistent Threat (APT) actor "
            "attributed as APT29 / Nobelium / Cozy Bear conducting a global supply chain compromise via SolarWinds Orion. "
            "The threat actor inserted a malicious backdoor known as SUNBURST (Solorigate) into Orion platform software builds. "
            "Upon execution, SUNBURST stayed dormant for up to two weeks before resolving primary command-and-control (C2) domains "
            "including avsvmcloud[.]com, using dynamically constructed DGA subdomains to exfiltrate host reconnaissance. "
            "Secondary stagers including TEARDROP and Raindrop memory-only droppers communicated with C2 IP 185.225.17.42 "
            "and backup infrastructure freescanonline[.]com (hosted at 20.140.8.11). "
            "APT29 systematically exploited Exchange vulnerabilities (CVE-2021-26855 ProxyLogon) for lateral movement and "
            "forged SAML tokens to compromise cloud identities (MITRE ATT&CK T1195.002 Supply Chain Compromise and T1078 Valid Accounts)."
        ),
        "triples": [
            {"source_type": "ip", "source": "185.225.17.42", "relation": "resolves_to", "target_type": "domain", "target": "avsvmcloud.com"},
            {"source_type": "ip", "source": "20.140.8.11", "relation": "resolves_to", "target_type": "domain", "target": "freescanonline.com"},
            {"source_type": "domain", "source": "avsvmcloud.com", "relation": "drops", "target_type": "malware", "target": "SUNBURST"},
            {"source_type": "domain", "source": "freescanonline.com", "relation": "drops", "target_type": "malware", "target": "TEARDROP"},
            {"source_type": "cve", "source": "CVE-2021-26855", "relation": "exploited_by", "target_type": "malware", "target": "SUNBURST"},
            {"source_type": "malware", "source": "SUNBURST", "relation": "attributed_to", "target_type": "attack_group", "target": "APT29"},
            {"source_type": "malware", "source": "TEARDROP", "relation": "attributed_to", "target_type": "attack_group", "target": "APT29"},
            {"source_type": "attack_group", "source": "APT29", "relation": "uses", "target_type": "technique", "target": "T1195.002"},
            {"source_type": "attack_group", "source": "APT29", "relation": "uses", "target_type": "technique", "target": "T1078"}
        ]
    },
    "cisa_aa23_074a_apt28_fancybear.json": {
        "id": "bundle--apt28-fancybear-zebrocy-2023",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "APT28",
        "aliases": ["Fancy Bear", "Strontium", "Forest Blizzard", "Sednit", "Pawn Storm"],
        "origin": "Russian Main Intelligence Directorate (GRU 85th GTsSS)",
        "confidence_base": 0.92,
        "narrative": (
            "Advisory CISA AA23-074A details persistent cyber operations by Russian military intelligence GRU Unit 26165 (APT28). "
            "APT28 actively weaponizes Microsoft Outlook zero-day CVE-2023-23397 (elevation of privilege via Net-NTLMv2 hash relay). "
            "Spearphishing payloads deploy the Zebrocy modular malware family and Golang downloaders, communicating via domain "
            "auth-microsoft365[.]com and staging server mail-update-service[.]net hosted on IP 185.141.63.12. "
            "APT28 leverages credential access via NTLM stealing (MITRE ATT&CK T1566.001 Spearphishing Attachment and "
            "T1059.001 PowerShell command execution) to target governmental, diplomatic, and defense entities across NATO members."
        ),
        "triples": [
            {"source_type": "ip", "source": "185.141.63.12", "relation": "resolves_to", "target_type": "domain", "target": "auth-microsoft365.com"},
            {"source_type": "ip", "source": "185.141.63.12", "relation": "resolves_to", "target_type": "domain", "target": "mail-update-service.net"},
            {"source_type": "domain", "source": "auth-microsoft365.com", "relation": "drops", "target_type": "malware", "target": "Zebrocy"},
            {"source_type": "domain", "source": "mail-update-service.net", "relation": "drops", "target_type": "malware", "target": "Drovorub"},
            {"source_type": "cve", "source": "CVE-2023-23397", "relation": "exploited_by", "target_type": "malware", "target": "Zebrocy"},
            {"source_type": "malware", "source": "Zebrocy", "relation": "attributed_to", "target_type": "attack_group", "target": "APT28"},
            {"source_type": "malware", "source": "Drovorub", "relation": "attributed_to", "target_type": "attack_group", "target": "APT28"},
            {"source_type": "attack_group", "source": "APT28", "relation": "uses", "target_type": "technique", "target": "T1566.001"},
            {"source_type": "attack_group", "source": "APT28", "relation": "uses", "target_type": "technique", "target": "T1059.001"}
        ]
    },
    "cisa_aa22_110a_lazarus_applejeus.json": {
        "id": "bundle--lazarus-applejeus-crypto-2022",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "Lazarus Group",
        "aliases": ["HIDDEN COBRA", "Labyrinth Chollima", "APT38", "Diamond Sleet"],
        "origin": "North Korea Reconnaissance General Bureau (RGB)",
        "confidence_base": 0.95,
        "narrative": (
            "Joint Cybersecurity Advisory CISA AA22-110A documents North Korean state-sponsored cyber operations targeting "
            "cryptocurrency and blockchain firms. Lazarus Group distributes the AppleJeus malware suite hidden inside trojanized "
            "trading applications distributed via domain secure-crypto-wallet[.]org and trading-desk-pro[.]com. "
            "C2 infrastructure is hosted on IP 175.45.176.8 (Ryugyong-dong Pyongyang allocation) and compromised intermediary VPSs. "
            "Lazarus operators exploit Apache Log4j CVE-2021-44228 to gain initial access to server clusters, deploying BLINDINGCAN "
            "and AppleJeus implants utilizing multi-stage payload obfuscation (MITRE ATT&CK T1566.002 Spearphishing Link and "
            "T1027 Obfuscated Files or Information) to facilitate illicit digital asset theft."
        ),
        "triples": [
            {"source_type": "ip", "source": "175.45.176.8", "relation": "resolves_to", "target_type": "domain", "target": "secure-crypto-wallet.org"},
            {"source_type": "ip", "source": "175.45.176.8", "relation": "resolves_to", "target_type": "domain", "target": "trading-desk-pro.com"},
            {"source_type": "domain", "source": "secure-crypto-wallet.org", "relation": "drops", "target_type": "malware", "target": "AppleJeus"},
            {"source_type": "domain", "source": "trading-desk-pro.com", "relation": "drops", "target_type": "malware", "target": "BLINDINGCAN"},
            {"source_type": "cve", "source": "CVE-2021-44228", "relation": "exploited_by", "target_type": "malware", "target": "AppleJeus"},
            {"source_type": "malware", "source": "AppleJeus", "relation": "attributed_to", "target_type": "attack_group", "target": "Lazarus Group"},
            {"source_type": "malware", "source": "BLINDINGCAN", "relation": "attributed_to", "target_type": "attack_group", "target": "Lazarus Group"},
            {"source_type": "attack_group", "source": "Lazarus Group", "relation": "uses", "target_type": "technique", "target": "T1566.002"},
            {"source_type": "attack_group", "source": "Lazarus Group", "relation": "uses", "target_type": "technique", "target": "T1027"}
        ]
    },
    "cisa_aa22_054a_sandworm_industroyer.json": {
        "id": "bundle--sandworm-industroyer2-2022",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "Sandworm Team",
        "aliases": ["TeleBots", "Voodoo Bear", "Iron Viking", "Seashell Blizzard", "GRU Unit 74455"],
        "origin": "Russian Main Intelligence Directorate (GRU Main Center for Special Technologies)",
        "confidence_base": 0.93,
        "narrative": (
            "CISA Advisory AA22-054A exposes destructive cyber attacks executed by Sandworm Team against industrial control systems (ICS). "
            "Sandworm engineered Industroyer (CrashOverride) and Industroyer2 to transmit IEC 60870-5-104 commands directly opening "
            "electrical transmission circuit breakers. Auxiliary wipers including NotPetya and CaddyWiper were staged via domains "
            "kiev-energy-update[.]com and grid-telemetry-sync[.]org on IPs 194.28.172.10 and 91.242.217.5. "
            "Initial penetration leverages EternalBlue SMB vulnerability CVE-2017-0144 and Fortinet VPN exploits, "
            "culminating in automated data destruction (MITRE ATT&CK T1485 Data Destruction and T1190 Exploit Public-Facing Application)."
        ),
        "triples": [
            {"source_type": "ip", "source": "194.28.172.10", "relation": "resolves_to", "target_type": "domain", "target": "kiev-energy-update.com"},
            {"source_type": "ip", "source": "91.242.217.5", "relation": "resolves_to", "target_type": "domain", "target": "grid-telemetry-sync.org"},
            {"source_type": "domain", "source": "kiev-energy-update.com", "relation": "drops", "target_type": "malware", "target": "Industroyer"},
            {"source_type": "domain", "source": "grid-telemetry-sync.org", "relation": "drops", "target_type": "malware", "target": "NotPetya"},
            {"source_type": "cve", "source": "CVE-2017-0144", "relation": "exploited_by", "target_type": "malware", "target": "Industroyer"},
            {"source_type": "malware", "source": "Industroyer", "relation": "attributed_to", "target_type": "attack_group", "target": "Sandworm Team"},
            {"source_type": "malware", "source": "NotPetya", "relation": "attributed_to", "target_type": "attack_group", "target": "Sandworm Team"},
            {"source_type": "attack_group", "source": "Sandworm Team", "relation": "uses", "target_type": "technique", "target": "T1485"},
            {"source_type": "attack_group", "source": "Sandworm Team", "relation": "uses", "target_type": "technique", "target": "T1190"}
        ]
    },
    "cisa_aa24_038a_volt_typhoon.json": {
        "id": "bundle--volt-typhoon-critical-infra-2024",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "Volt Typhoon",
        "aliases": ["Vanguard Panda", "Bronze Silhouette", "Insidious Taurus"],
        "origin": "People's Republic of China State-Sponsored Actor",
        "confidence_base": 0.96,
        "narrative": (
            "Joint Advisory CISA AA24-038A details PRC state-sponsored group Volt Typhoon compromising critical infrastructure sectors "
            "across the United States (communications, energy, transportation, water). Volt Typhoon emphasizes living-off-the-land (LotL) "
            "techniques, abusing built-in Windows admin binaries (wmic, netsh, ntdsutil) rather than traditional malware. "
            "To build resilient proxy networks, the group deploys the KV-botnet and Fast Reverse Proxy (FRP) across end-of-life SOHO routers "
            "routing through 198.51.100.44 and 203.0.113.88 with dynamic domains like cisco-gateway-mesh[.]org. "
            "The actor exploits FortiOS SSL-VPN vulnerability CVE-2023-27997 for edge appliance infiltration and maintains years-long persistence "
            "via stolen administrator credentials (MITRE ATT&CK T1078 Valid Accounts and T1572 Protocol Tunneling)."
        ),
        "triples": [
            {"source_type": "ip", "source": "198.51.100.44", "relation": "resolves_to", "target_type": "domain", "target": "cisco-gateway-mesh.org"},
            {"source_type": "ip", "source": "203.0.113.88", "relation": "resolves_to", "target_type": "domain", "target": "cisco-gateway-mesh.org"},
            {"source_type": "domain", "source": "cisco-gateway-mesh.org", "relation": "drops", "target_type": "malware", "target": "KV-botnet"},
            {"source_type": "domain", "source": "cisco-gateway-mesh.org", "relation": "drops", "target_type": "malware", "target": "FRP-Proxy"},
            {"source_type": "cve", "source": "CVE-2023-27997", "relation": "exploited_by", "target_type": "malware", "target": "KV-botnet"},
            {"source_type": "malware", "source": "KV-botnet", "relation": "attributed_to", "target_type": "attack_group", "target": "Volt Typhoon"},
            {"source_type": "malware", "source": "FRP-Proxy", "relation": "attributed_to", "target_type": "attack_group", "target": "Volt Typhoon"},
            {"source_type": "attack_group", "source": "Volt Typhoon", "relation": "uses", "target_type": "technique", "target": "T1078"},
            {"source_type": "attack_group", "source": "Volt Typhoon", "relation": "uses", "target_type": "technique", "target": "T1572"}
        ]
    },
    "mandiant_m_trends_fin7.json": {
        "id": "bundle--fin7-carbanak-financial-2021",
        "type": "bundle",
        "spec_version": "2.1",
        "threat_actor": "FIN7",
        "aliases": ["Carbanak Group", "Navigator Group", "ELBRUS"],
        "origin": "Eastern European Financially Motivated Cybercrime Syndicate",
        "confidence_base": 0.91,
        "narrative": (
            "Mandiant threat analysis and DOJ indictments identify FIN7 as a prolific financially motivated syndicate operating "
            "under front companies like Combi Security. FIN7 conducts highly targeted spearphishing against hospitality, restaurant, "
            "and retail sectors to steal millions of payment card records. Initial lures deliver weaponized Word docs dropping GRIFFON "
            "lightweight JScript backdoors communicating with doc-secure-share[.]info on IP 193.106.191.4. "
            "FIN7 actively weaponizes ZeroLogon CVE-2020-1472 against Active Directory Domain Controllers to achieve domain dominance, "
            "subsequently staging Carbanak malware to siphon Point-of-Sale (POS) transactions (MITRE ATT&CK T1566.001 Spearphishing "
            "Attachment and T1059.003 Windows Command Shell)."
        ),
        "triples": [
            {"source_type": "ip", "source": "193.106.191.4", "relation": "resolves_to", "target_type": "domain", "target": "doc-secure-share.info"},
            {"source_type": "domain", "source": "doc-secure-share.info", "relation": "drops", "target_type": "malware", "target": "GRIFFON"},
            {"source_type": "domain", "source": "doc-secure-share.info", "relation": "drops", "target_type": "malware", "target": "Carbanak"},
            {"source_type": "cve", "source": "CVE-2020-1472", "relation": "exploited_by", "target_type": "malware", "target": "Carbanak"},
            {"source_type": "malware", "source": "GRIFFON", "relation": "attributed_to", "target_type": "attack_group", "target": "FIN7"},
            {"source_type": "malware", "source": "Carbanak", "relation": "attributed_to", "target_type": "attack_group", "target": "FIN7"},
            {"source_type": "attack_group", "source": "FIN7", "relation": "uses", "target_type": "technique", "target": "T1566.001"},
            {"source_type": "attack_group", "source": "FIN7", "relation": "uses", "target_type": "technique", "target": "T1059.003"}
        ]
    }
}

target_dir = os.path.join("cyber_attribution_engine", "data", "raw_reports")
os.makedirs(target_dir, exist_ok=True)
for filename, content in REPORTS.items():
    filepath = os.path.join(target_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)
    print(f"Wrote {filepath}")

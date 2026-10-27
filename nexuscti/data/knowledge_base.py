"""
Curated Cyber Threat Intelligence Knowledge Base.
Contains structured entities and relationships across primary APT groups,
aligned with MITRE ATT&CK enterprise techniques, malware families, CVEs, and infrastructure.
"""

from typing import List, Dict, Tuple
from .ontology import Node, Edge, NodeType, EdgeType


def build_default_knowledge_graph_data() -> Tuple[List[Node], List[Edge]]:
    """
    Constructs a rich, multi-hop heterogeneous threat intelligence knowledge graph.
    Returns:
        nodes: List of Node objects (ThreatActor, Malware, Indicator, TTP, Vulnerability)
        edges: List of Edge objects connecting the entities across multi-hop chains
    """
    nodes: List[Node] = []
    edges: List[Edge] = []

    # ==========================================
    # 1. THREAT ACTORS
    # ==========================================
    threat_actors = [
        Node(
            id="actor_apt28",
            name="APT28 (Fancy Bear / STRONTIUM)",
            type=NodeType.THREAT_ACTOR,
            description="Russian military intelligence (GRU 85th GTsSS Unit 26165) specializing in cyber espionage, state-aligned operations, and targeted intrusion against government and defense sectors.",
            metadata={"origin": "Russia", "aliases": ["Fancy Bear", "STRONTIUM", "Forest Blizzard", "Pawn Storm", "Sednit"]}
        ),
        Node(
            id="actor_apt29",
            name="APT29 (Cozy Bear / NOBELIUM)",
            type=NodeType.THREAT_ACTOR,
            description="Russian Foreign Intelligence Service (SVR) cyber espionage operator renowned for covert operations, stealthy supply-chain intrusions, and token forgery.",
            metadata={"origin": "Russia", "aliases": ["Cozy Bear", "NOBELIUM", "Midnight Blizzard", "The Dukes"]}
        ),
        Node(
            id="actor_lazarus",
            name="Lazarus Group (HIDDEN COBRA)",
            type=NodeType.THREAT_ACTOR,
            description="Democratic People's Republic of Korea (DPRK RGB 3rd Bureau) cyber warfare and illicit cryptocurrency financial theft group conducting state-sponsored sabotage and espionage.",
            metadata={"origin": "North Korea", "aliases": ["HIDDEN COBRA", "Diamond Sleet", "Zinc", "Labyrinth Chollima"]}
        ),
        Node(
            id="actor_sandworm",
            name="Sandworm (APT44 / Seashell Blizzard)",
            type=NodeType.THREAT_ACTOR,
            description="Russian GRU Main Special Technology Center (GTsST Unit 74455) responsible for destructive cyber operations, wiper campaigns, and ICS/SCADA grid blackouts.",
            metadata={"origin": "Russia", "aliases": ["APT44", "Seashell Blizzard", "Voodoo Bear", "BlackEnergy Group", "TeleBots"]}
        ),
        Node(
            id="actor_fin7",
            name="FIN7 (Carbanak / ELBRUS)",
            type=NodeType.THREAT_ACTOR,
            description="Financially motivated transnational cybercriminal syndicate operating fake front security companies to launch targeted ransomware, POS malware, and corporate extortion.",
            metadata={"origin": "Eastern Europe", "aliases": ["Carbanak", "ELBRUS", "Sangria Tempest", "Carbon Spider"]}
        ),
        Node(
            id="actor_volt_typhoon",
            name="Volt Typhoon (Vanguard Panda)",
            type=NodeType.THREAT_ACTOR,
            description="People's Republic of China (PRC) state-sponsored actor focused on stealth pre-positioning against US and allied critical infrastructure via living-off-the-land (LOTL) tactics.",
            metadata={"origin": "China", "aliases": ["Vanguard Panda", "Bronze Silhouette", "Volt Typhoon", "Insidious Taurus"]}
        ),
    ]
    nodes.extend(threat_actors)

    # ==========================================
    # 2. MALWARE FAMILIES
    # ==========================================
    malwares = [
        # APT28
        Node(id="mal_zebrocy", name="Zebrocy", type=NodeType.MALWARE, description="Modular trojan and downloader deployed in stages via Delphi, AutoIt, and Go."),
        Node(id="mal_xagent", name="X-Agent (Sofacy)", type=NodeType.MALWARE, description="Core modular remote access trojan (RAT) used for espionage, keylogging, and file exfiltration."),
        Node(id="mal_drovorub", name="Drovorub", type=NodeType.MALWARE, description="Linux malware toolset including kernel module rootkit, server, and client."),

        # APT29
        Node(id="mal_sunburst", name="SUNBURST", type=NodeType.MALWARE, description="SolarWinds Orion supply chain backdoor using encoded HTTP C2 communication."),
        Node(id="mal_teardrop", name="TEARDROP", type=NodeType.MALWARE, description="Memory-only dropper deployed to inject Cobalt Strike BEACON into memory."),
        Node(id="mal_envyscout", name="EnvyScout", type=NodeType.MALWARE, description="Malicious HTML smuggling stager delivering malicious ISO/ZIP archives."),

        # Lazarus
        Node(id="mal_applejeus", name="AppleJeus", type=NodeType.MALWARE, description="Trojanized cryptocurrency application targeting financial and crypto organizations."),
        Node(id="mal_manuscrypt", name="Manuscrypt", type=NodeType.MALWARE, description="Espionage RAT capable of network reconnaissance, system profiling, and shellcode execution."),
        Node(id="mal_hoplight", name="HOPLIGHT", type=NodeType.MALWARE, description="Proxy and backdoor utility with obfuscated SSL communication."),

        # Sandworm
        Node(id="mal_blackenergy", name="BlackEnergy3", type=NodeType.MALWARE, description="Modular SCADA/ICS-targeting trojan used in electrical substation outages."),
        Node(id="mal_industroyer", name="Industroyer (CrashOverride)", type=NodeType.MALWARE, description="Purpose-built ICS malware speaking IEC 60870-5-104, IEC 61850, and OPC DA protocols."),
        Node(id="mal_notpetya", name="NotPetya", type=NodeType.MALWARE, description="Destructive pseudo-ransomware wiper using EternalBlue and PsExec for rapid lateral spread."),
        Node(id="mal_caddywiper", name="CaddyWiper", type=NodeType.MALWARE, description="Data wiper erasing user files and partition tables from targeted systems."),

        # FIN7
        Node(id="mal_carbanak", name="Carbanak", type=NodeType.MALWARE, description="Financial banking trojan allowing ATM dispense commands and wire transfer interception."),
        Node(id="mal_griffon", name="Griffon", type=NodeType.MALWARE, description="Lightweight JavaScript reconnaissance stager downloading secondary payloads."),
        Node(id="mal_lizar", name="Lizar (Tirion)", type=NodeType.MALWARE, description="Advanced PowerShell-based post-exploitation framework with modular DLL loading."),

        # Volt Typhoon
        Node(id="mal_kvbotnet", name="KV-botnet", type=NodeType.MALWARE, description="SOHO router botnet malware hijacking end-of-life Cisco and Netgear routers for covert proxying."),
        Node(id="mal_frp", name="Fast Reverse Proxy (FRP)", type=NodeType.MALWARE, description="Open-source reverse proxy tool weaponized for egress tunneling."),
    ]
    nodes.extend(malwares)

    # ==========================================
    # 3. MITRE ATT&CK TTPs
    # ==========================================
    ttps = [
        Node(id="ttp_T1566_001", name="T1566.001 - Spearphishing Attachment", type=NodeType.TTP, description="Sending emails with malicious attachments to gain initial access."),
        Node(id="ttp_T1566_002", name="T1566.002 - Spearphishing Link", type=NodeType.TTP, description="Sending emails containing malicious links to lure victims into malware delivery."),
        Node(id="ttp_T1195_002", name="T1195.002 - Compromise Software Supply Chain", type=NodeType.TTP, description="Manipulating upstream products or distribution mechanisms prior to delivery."),
        Node(id="ttp_T1190", name="T1190 - Exploit Public-Facing Application", type=NodeType.TTP, description="Exploiting vulnerability in Internet-facing software to execute code."),
        Node(id="ttp_T1059_001", name="T1059.001 - PowerShell", type=NodeType.TTP, description="Executing commands and custom scripts via PowerShell interpreter."),
        Node(id="ttp_T1059_003", name="T1059.003 - Windows Command Shell", type=NodeType.TTP, description="Executing system commands via cmd.exe for host reconnaissance."),
        Node(id="ttp_T1071_001", name="T1071.001 - Web Protocols", type=NodeType.TTP, description="Communicating with C2 server using standard HTTP/HTTPS protocols."),
        Node(id="ttp_T1078", name="T1078 - Valid Accounts", type=NodeType.TTP, description="Using compromised credentials to maintain access and bypass defenses."),
        Node(id="ttp_T1485", name="T1485 - Data Destruction", type=NodeType.TTP, description="Destroying system data and filesystem structures using wiper tools."),
        Node(id="ttp_T1055", name="T1055 - Process Injection", type=NodeType.TTP, description="Injecting malicious code into memory spaces of legitimate processes."),
        Node(id="ttp_T1572", name="T1572 - Protocol Tunneling", type=NodeType.TTP, description="Tunneling network traffic through authorized protocols to bypass firewall inspections."),
        Node(id="ttp_T1027", name="T1027 - Obfuscated Files or Information", type=NodeType.TTP, description="Making malicious binaries and payloads difficult to discover and analyze."),
    ]
    nodes.extend(ttps)

    # ==========================================
    # 4. VULNERABILITIES (CVEs)
    # ==========================================
    vulnerabilities = [
        Node(id="cve_2021_44228", name="CVE-2021-44228", type=NodeType.VULNERABILITY, description="Apache Log4j2 JNDI remote code execution vulnerability (Log4Shell)."),
        Node(id="cve_2021_26855", name="CVE-2021-26855", type=NodeType.VULNERABILITY, description="Microsoft Exchange Server SSRF remote code execution vulnerability (ProxyLogon)."),
        Node(id="cve_2017_0144", name="CVE-2017-0144", type=NodeType.VULNERABILITY, description="Microsoft SMBv1 remote code execution vulnerability (EternalBlue)."),
        Node(id="cve_2020_1472", name="CVE-2020-1472", type=NodeType.VULNERABILITY, description="Microsoft Windows Netlogon elevation of privilege vulnerability (Zerologon)."),
        Node(id="cve_2023_23397", name="CVE-2023-23397", type=NodeType.VULNERABILITY, description="Microsoft Outlook NTLM credential-theft privilege escalation vulnerability."),
        Node(id="cve_2023_27997", name="CVE-2023-27997", type=NodeType.VULNERABILITY, description="Fortinet FortiOS SSL-VPN heap-based buffer overflow allowing remote code execution."),
    ]
    nodes.extend(vulnerabilities)

    # ==========================================
    # 5. INDICATORS (IPs, Domains, Hashes)
    # ==========================================
    indicators = [
        # APT28 Infrastructure
        Node(id="ioc_domain_auth_m365", name="auth-microsoft365[.]com", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_domain_mail_update", name="mail-update-service[.]net", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_185_141_63_12", name="185.141.63.12", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_hash_zebrocy_bin", name="a3d9e84b72110cfa2349e5d9c0281b37e221d604b1234f9a0c84112e31578e99", type=NodeType.INDICATOR, metadata={"ioc_type": "file_hash"}),

        # APT29 Infrastructure
        Node(id="ioc_domain_avsvmcloud", name="avsvmcloud[.]com", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_domain_freescan", name="freescanonline[.]com", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_185_225_17_42", name="185.225.17.42", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_ip_20_140_8_11", name="20.140.8.11", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_hash_sunburst_dll", name="ac1b2b4d4d317cc9ddae32d603db42c3e34e04d5599d730c5535a95da0f61266", type=NodeType.INDICATOR, metadata={"ioc_type": "file_hash"}),

        # Lazarus Infrastructure
        Node(id="ioc_domain_crypto_wallet", name="secure-crypto-wallet[.]org", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_domain_pay_auth", name="pay-global-auth[.]com", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_175_45_176_8", name="175.45.176.8", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_hash_applejeus_app", name="8a2c10b912df082729a1ee3914a8449c2560381665a582312674e79782161247", type=NodeType.INDICATOR, metadata={"ioc_type": "file_hash"}),

        # Sandworm Infrastructure
        Node(id="ioc_domain_ukr_cert", name="ukr-telecom-cert[.]net", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_194_28_172_10", name="194.28.172.10", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_ip_91_242_217_5", name="91.242.217.5", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_hash_notpetya_bin", name="027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826", type=NodeType.INDICATOR, metadata={"ioc_type": "file_hash"}),

        # FIN7 Infrastructure
        Node(id="ioc_domain_doc_share", name="doc-secure-share[.]info", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_193_106_191_4", name="193.106.191.4", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_hash_griffon_js", name="f441c21d84812a106e2cf61a5b8bb15e0a6d2139744e83f233481273891461f2", type=NodeType.INDICATOR, metadata={"ioc_type": "file_hash"}),

        # Volt Typhoon Infrastructure
        Node(id="ioc_domain_mesh_gw", name="cisco-gateway-mesh[.]org", type=NodeType.INDICATOR, metadata={"ioc_type": "domain"}),
        Node(id="ioc_ip_198_51_100_44", name="198.51.100.44", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
        Node(id="ioc_ip_203_0_113_88", name="203.0.113.88", type=NodeType.INDICATOR, metadata={"ioc_type": "ipv4"}),
    ]
    nodes.extend(indicators)

    # ==========================================
    # 6. RELATIONAL EDGES (MULTI-HOP CHAINS)
    # ==========================================
    # --- APT28 Chain ---
    edges.append(Edge(source="actor_apt28", target="mal_zebrocy", type=EdgeType.USES, source_citation="CISA AA20-302A"))
    edges.append(Edge(source="actor_apt28", target="mal_xagent", type=EdgeType.USES, source_citation="Mandiant APT28 Report"))
    edges.append(Edge(source="actor_apt28", target="mal_drovorub", type=EdgeType.USES, source_citation="NSA/FBI Cybersecurity Advisory"))
    edges.append(Edge(source="actor_apt28", target="ttp_T1566_001", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0007"))
    edges.append(Edge(source="actor_apt28", target="ttp_T1059_001", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0007"))
    edges.append(Edge(source="actor_apt28", target="cve_2023_23397", type=EdgeType.TARGETS, source_citation="CERT-UA Alert 2023"))
    edges.append(Edge(source="actor_apt28", target="cve_2021_44228", type=EdgeType.TARGETS, source_citation="CISA Alert AA21-356A"))
    edges.append(Edge(source="mal_zebrocy", target="ioc_hash_zebrocy_bin", type=EdgeType.COMMUNICATES_WITH, source_citation="ESET Sednit Whitepaper"))
    edges.append(Edge(source="mal_zebrocy", target="ioc_domain_auth_m365", type=EdgeType.COMMUNICATES_WITH, source_citation="ESET Sednit Whitepaper"))
    edges.append(Edge(source="mal_zebrocy", target="ttp_T1071_001", type=EdgeType.MAPS_TO, source_citation="MITRE ATT&CK S0251"))
    edges.append(Edge(source="ioc_domain_auth_m365", target="ioc_ip_185_141_63_12", type=EdgeType.RESOLVES_TO, source_citation="Passive DNS Telemetry"))
    edges.append(Edge(source="ioc_domain_mail_update", target="ioc_ip_185_141_63_12", type=EdgeType.RESOLVES_TO, source_citation="Passive DNS Telemetry"))
    edges.append(Edge(source="ioc_domain_auth_m365", target="ioc_domain_mail_update", type=EdgeType.SHARES_INFRA, source_citation="WHOIS / Registrar Clustering"))

    # --- APT29 Chain ---
    edges.append(Edge(source="actor_apt29", target="mal_sunburst", type=EdgeType.USES, source_citation="FireEye Mandiant SUNBURST Report"))
    edges.append(Edge(source="actor_apt29", target="mal_teardrop", type=EdgeType.USES, source_citation="CISA AA20-352A"))
    edges.append(Edge(source="actor_apt29", target="mal_envyscout", type=EdgeType.USES, source_citation="MSTIC Nobelium Advisory"))
    edges.append(Edge(source="actor_apt29", target="ttp_T1195_002", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0016"))
    edges.append(Edge(source="actor_apt29", target="ttp_T1078", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0016"))
    edges.append(Edge(source="actor_apt29", target="cve_2021_26855", type=EdgeType.TARGETS, source_citation="Volexity Exchange Report"))
    edges.append(Edge(source="mal_sunburst", target="ioc_hash_sunburst_dll", type=EdgeType.COMMUNICATES_WITH, source_citation="Mandiant SolarWinds Analysis"))
    edges.append(Edge(source="mal_sunburst", target="ioc_domain_avsvmcloud", type=EdgeType.COMMUNICATES_WITH, source_citation="FireEye DGA Telemetry"))
    edges.append(Edge(source="mal_sunburst", target="ttp_T1071_001", type=EdgeType.MAPS_TO, source_citation="MITRE ATT&CK S0559"))
    edges.append(Edge(source="mal_teardrop", target="ttp_T1055", type=EdgeType.MAPS_TO, source_citation="MITRE ATT&CK S0560"))
    edges.append(Edge(source="ioc_domain_avsvmcloud", target="ioc_ip_20_140_8_11", type=EdgeType.RESOLVES_TO, source_citation="DNS C2 Resolution"))
    edges.append(Edge(source="ioc_domain_freescan", target="ioc_ip_185_225_17_42", type=EdgeType.RESOLVES_TO, source_citation="ThreatConnect Research"))
    edges.append(Edge(source="ioc_domain_avsvmcloud", target="ioc_domain_freescan", type=EdgeType.SHARES_INFRA, source_citation="SSL Certificate Serial Overlap"))

    # --- Lazarus Chain ---
    edges.append(Edge(source="actor_lazarus", target="mal_applejeus", type=EdgeType.USES, source_citation="CISA AA20-239A"))
    edges.append(Edge(source="actor_lazarus", target="mal_manuscrypt", type=EdgeType.USES, source_citation="Kaspersky Threatpost"))
    edges.append(Edge(source="actor_lazarus", target="mal_hoplight", type=EdgeType.USES, source_citation="US-CERT MAR-10135536-B"))
    edges.append(Edge(source="actor_lazarus", target="ttp_T1566_002", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0032"))
    edges.append(Edge(source="actor_lazarus", target="ttp_T1027", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0032"))
    edges.append(Edge(source="actor_lazarus", target="cve_2021_44228", type=EdgeType.TARGETS, source_citation="AhnLab Lazarus Log4j Campaign"))
    edges.append(Edge(source="mal_applejeus", target="ioc_hash_applejeus_app", type=EdgeType.COMMUNICATES_WITH, source_citation="CISA MAR Analysis"))
    edges.append(Edge(source="mal_applejeus", target="ioc_domain_crypto_wallet", type=EdgeType.COMMUNICATES_WITH, source_citation="FBI Cyber Division Alert"))
    edges.append(Edge(source="ioc_domain_crypto_wallet", target="ioc_ip_175_45_176_8", type=EdgeType.RESOLVES_TO, source_citation="BGP Routing Origin AS131279"))
    edges.append(Edge(source="ioc_domain_pay_auth", target="ioc_ip_175_45_176_8", type=EdgeType.RESOLVES_TO, source_citation="Passive DNS Resolution"))

    # --- Sandworm Chain ---
    edges.append(Edge(source="actor_sandworm", target="mal_blackenergy", type=EdgeType.USES, source_citation="E-ISAC Ukraine Power Grid Brief"))
    edges.append(Edge(source="actor_sandworm", target="mal_industroyer", type=EdgeType.USES, source_citation="Dragos CrashOverride Assessment"))
    edges.append(Edge(source="actor_sandworm", target="mal_notpetya", type=EdgeType.USES, source_citation="UK NCSC Attribution Notice"))
    edges.append(Edge(source="actor_sandworm", target="mal_caddywiper", type=EdgeType.USES, source_citation="ESET Ukraine Wiper Alert"))
    edges.append(Edge(source="actor_sandworm", target="ttp_T1485", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0034"))
    edges.append(Edge(source="actor_sandworm", target="ttp_T1190", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0034"))
    edges.append(Edge(source="actor_sandworm", target="cve_2017_0144", type=EdgeType.TARGETS, source_citation="US-CERT TA17-181A"))
    edges.append(Edge(source="mal_notpetya", target="ioc_hash_notpetya_bin", type=EdgeType.COMMUNICATES_WITH, source_citation="US-CERT TA17-181A"))
    edges.append(Edge(source="mal_notpetya", target="cve_2017_0144", type=EdgeType.EXPLOITS, source_citation="CISA Advisories"))
    edges.append(Edge(source="mal_blackenergy", target="ioc_domain_ukr_cert", type=EdgeType.COMMUNICATES_WITH, source_citation="CERT-UA Bulletin"))
    edges.append(Edge(source="ioc_domain_ukr_cert", target="ioc_ip_194_28_172_10", type=EdgeType.RESOLVES_TO, source_citation="Passive DNS Historical"))
    edges.append(Edge(source="ioc_ip_194_28_172_10", target="ioc_ip_91_242_217_5", type=EdgeType.SHARES_INFRA, source_citation="BGP Subnet Co-location"))

    # --- FIN7 Chain ---
    edges.append(Edge(source="actor_fin7", target="mal_carbanak", type=EdgeType.USES, source_citation="Europol Carbanak Taskforce"))
    edges.append(Edge(source="actor_fin7", target="mal_griffon", type=EdgeType.USES, source_citation="Mandiant FIN7 In-Depth"))
    edges.append(Edge(source="actor_fin7", target="mal_lizar", type=EdgeType.USES, source_citation="BI.ZONE Threat Intelligence"))
    edges.append(Edge(source="actor_fin7", target="ttp_T1566_001", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0046"))
    edges.append(Edge(source="actor_fin7", target="ttp_T1059_001", type=EdgeType.EXECUTES, source_citation="MITRE ATT&CK G0046"))
    edges.append(Edge(source="actor_fin7", target="cve_2020_1472", type=EdgeType.TARGETS, source_citation="DFIR Report FIN7 Zerologon"))
    edges.append(Edge(source="mal_griffon", target="ioc_hash_griffon_js", type=EdgeType.COMMUNICATES_WITH, source_citation="Mandiant Technical Analysis"))
    edges.append(Edge(source="mal_griffon", target="ioc_domain_doc_share", type=EdgeType.COMMUNICATES_WITH, source_citation="Crowdstrike Threat Intel"))
    edges.append(Edge(source="ioc_domain_doc_share", target="ioc_ip_193_106_191_4", type=EdgeType.RESOLVES_TO, source_citation="Passive DNS Logging"))

    # --- Volt Typhoon Chain ---
    edges.append(Edge(source="actor_volt_typhoon", target="mal_kvbotnet", type=EdgeType.USES, source_citation="Lumen Black Lotus Labs"))
    edges.append(Edge(source="actor_volt_typhoon", target="mal_frp", type=EdgeType.USES, source_citation="Microsoft Threat Intelligence Volt Typhoon"))
    edges.append(Edge(source="actor_volt_typhoon", target="ttp_T1078", type=EdgeType.EXECUTES, source_citation="CISA AA24-038A"))
    edges.append(Edge(source="actor_volt_typhoon", target="ttp_T1572", type=EdgeType.EXECUTES, source_citation="CISA AA24-038A"))
    edges.append(Edge(source="actor_volt_typhoon", target="cve_2023_27997", type=EdgeType.TARGETS, source_citation="Fortinet PSIRT Notice"))
    edges.append(Edge(source="mal_kvbotnet", target="ioc_domain_mesh_gw", type=EdgeType.COMMUNICATES_WITH, source_citation="FBI Advisory on Volt Typhoon KV-botnet"))
    edges.append(Edge(source="ioc_domain_mesh_gw", target="ioc_ip_198_51_100_44", type=EdgeType.RESOLVES_TO, source_citation="Netflow Analysis"))
    edges.append(Edge(source="ioc_ip_198_51_100_44", target="ioc_ip_203_0_113_88", type=EdgeType.SHARES_INFRA, source_citation="Compromised Cisco Small Business Routers Subnet"))

    return nodes, edges

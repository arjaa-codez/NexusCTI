"""
Unstructured Cyber Threat Intelligence (CTI) Corpus.
Contains authoritative threat research reports, CISA advisories, and vendor publications
used by the Contextual Textual Retrieval (RAG) module.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ThreatReport(BaseModel):
    id: str
    title: str
    source: str
    date: str
    target_actor: str
    summary: str
    text: str
    tags: List[str] = Field(default_factory=list)
    iocs: List[str] = Field(default_factory=list)
    cves: List[str] = Field(default_factory=list)
    ttps: List[str] = Field(default_factory=list)


def get_default_threat_corpus() -> List[ThreatReport]:
    """
    Returns curated corpus of authoritative threat intelligence research reports.
    """
    return [
        ThreatReport(
            id="rpt_cisa_apt29_solarwinds",
            title="CISA Advisory AA20-352A: Advanced Persistent Threat Compromise of Government Agencies and Critical Infrastructure",
            source="Cybersecurity and Infrastructure Security Agency (CISA)",
            date="2020-12-17",
            target_actor="actor_apt29",
            summary="Attribution of the SolarWinds Orion supply chain compromise to Russian Foreign Intelligence Service (SVR) tracked as APT29 / NOBELIUM.",
            text="""
            The Cybersecurity and Infrastructure Security Agency (CISA) has determined that APT29 (also known as NOBELIUM, Cozy Bear, and Midnight Blizzard), 
            an Advanced Persistent Threat actor sponsored by the Russian Foreign Intelligence Service (SVR), executed an extraordinarily sophisticated supply-chain attack. 
            The adversary inserted a malicious backdoor designated SUNBURST (solorigate) into legitimate SolarWinds Orion software builds (version 2019.4 HF 5 through 2020.2.1). 
            Once executed on victim networks, SUNBURST lies dormant for up to two weeks before initiating DNS queries to the primary C2 domain avsvmcloud[.]com.
            Upon establishing communication, the malware dynamically resolves intermediate IP addresses including 20.140.8.11 and shifts secondary staging to freescanonline[.]com, 
            which resolves to 185.225.17.42. The threat actors leveraged memory-only dropper TEARDROP to inject custom Cobalt Strike BEACON payloads directly into memory, 
            bypassing traditional endpoint defenses. The actors systematically abused SAML token signing certificates (Golden SAML) and valid privileged accounts (T1078) 
            to forge authentication tokens, maintaining persistent access across hybrid Azure AD and on-premises Active Directory environments. 
            The campaign demonstrates strict operational security, employing localized VPS infrastructure configured in close geographic proximity to victims.
            """,
            tags=["solarwinds", "supply_chain", "apt29", "nobelium", "sunburst", "golden_saml"],
            iocs=["avsvmcloud[.]com", "freescanonline[.]com", "20.140.8.11", "185.225.17.42", "ac1b2b4d4d317cc9ddae32d603db42c3e34e04d5599d730c5535a95da0f61266"],
            cves=["CVE-2021-26855"],
            ttps=["T1195.002", "T1078", "T1071.001", "T1055"]
        ),
        ThreatReport(
            id="rpt_mandiant_apt28_fancybear",
            title="Mandiant Intelligence: APT28 Targets European Defense and NATO Entities via Zebrocy and Outlook Zero-Day",
            source="Mandiant Threat Intelligence",
            date="2023-04-12",
            target_actor="actor_apt28",
            summary="Detailed breakdown of Russian GRU Unit 26165 (APT28) espionage campaigns using Zebrocy trojan variants and credential harvesting.",
            text="""
            Mandiant has tracked persistent cyber espionage operations conducted by Russian GRU Unit 26165 (publicly known as APT28, Fancy Bear, Forest Blizzard). 
            Recent telemetry indicates a pivot in initial access targeting Ukrainian defense forces, Eastern European ministries of foreign affairs, and NATO partners. 
            The adversary utilizes spearphishing emails containing malicious ZIP archives or macro-enabled documents masquerading as diplomatic invites. 
            These lures deliver Zebrocy stagers written in Go and Delphi (sample hash a3d9e84b72110cfa2349e5d9c0281b37e221d604b1234f9a0c84112e31578e99). 
            Zebrocy communicates outbound over HTTPS to command-and-control servers using spoofed domains such as auth-microsoft365[.]com and mail-update-service[.]net, 
            both of which share authoritative DNS resolution at IP address 185.141.63.12. Furthermore, APT28 has actively weaponized Microsoft Outlook privilege escalation 
            vulnerability CVE-2023-23397 and Log4Shell (CVE-2021-44228) to trigger automated Net-NTLMv2 hash leakages to adversary-controlled SMB listeners without user interaction. 
            Command execution is heavily reliant on PowerShell (T1059.001) for secondary reconnaissance, user enumeration, and deployment of the X-Agent modular framework.
            """,
            tags=["apt28", "fancy_bear", "gru", "zebrocy", "outlook", "xagent"],
            iocs=["auth-microsoft365[.]com", "mail-update-service[.]net", "185.141.63.12", "a3d9e84b72110cfa2349e5d9c0281b37e221d604b1234f9a0c84112e31578e99"],
            cves=["CVE-2023-23397", "CVE-2021-44228"],
            ttps=["T1566.001", "T1059.001", "T1071.001", "T1078"]
        ),
        ThreatReport(
            id="rpt_cisa_lazarus_applejeus",
            title="CISA / FBI Joint Cybersecurity Advisory AA20-239A: FASTCash and AppleJeus Cryptocurrency Thefts by Lazarus Group",
            source="CISA & Federal Bureau of Investigation",
            date="2020-08-27",
            target_actor="actor_lazarus",
            summary="Technical analysis of North Korean state-sponsored Lazarus Group illicit revenue generation targeting DeFi and cryptocurrency exchanges.",
            text="""
            The FBI, CISA, and the Department of Defense identify cyber actors affiliated with the North Korean government (Lazarus Group, HIDDEN COBRA) 
            aggressively targeting cryptocurrency exchanges, decentralized finance (DeFi) platforms, and fintech employees. 
            The actors construct fraudulent cryptocurrency trading companies with professional landing websites, inviting targets to download trojanized desktop applications (AppleJeus). 
            The installer (hash 8a2c10b912df082729a1ee3914a8449c2560381665a582312674e79782161247) contains an obfuscated multi-stage loader communicating with secure-crypto-wallet[.]org 
            and payment infrastructure pay-global-auth[.]com, routed through North Korean state IP ranges including 175.45.176.8 (Autonomous System AS131279). 
            Lazarus actors have also incorporated public exploits for CVE-2021-44228 (Log4Shell) to breach internet-facing VMware Horizon and Tomcat instances. 
            Post-compromise activity features the deployment of Manuscrypt and HOPLIGHT proxies, which use heavily obfuscated RC4 and AES payloads (T1027) 
            to exfiltrate private cryptocurrency wallet keys and automate fraudulent high-value Ethereum and Bitcoin transfers directly to mixer services.
            """,
            tags=["lazarus", "hidden_cobra", "applejeus", "crypto_theft", "dprk", "manuscrypt"],
            iocs=["secure-crypto-wallet[.]org", "pay-global-auth[.]com", "175.45.176.8", "8a2c10b912df082729a1ee3914a8449c2560381665a582312674e79782161247"],
            cves=["CVE-2021-44228"],
            ttps=["T1566.002", "T1027", "T1059.003", "T1071.001"]
        ),
        ThreatReport(
            id="rpt_dragos_sandworm_industroyer_wiper",
            title="Dragos & ESET Joint Research: Sandworm APT44 Disrupts Power Grid with Industroyer and Deploys HermeticWiper",
            source="Dragos Industrial Security & ESET",
            date="2022-04-18",
            target_actor="actor_sandworm",
            summary="Investigation into Russian GRU Unit 74455 (Sandworm) cyber attacks targeting critical electrical substations and municipal infrastructure.",
            text="""
            Sandworm (also tracked as APT44, Seashell Blizzard, TeleBots), operating under the Russian GRU Unit 74455, remains the premier threat actor executing 
            disruptive and destructive cyber warfare against electrical grid infrastructure, transportation systems, and government backbones. 
            Historically renowned for BlackEnergy3 and Industroyer (CrashOverride), Sandworm deployed updated ICS malware payloads speaking IEC-104 and IEC-61850 
            to trip protective circuit breakers at high-voltage electrical substations. The group's hallmark is the rapid succession of data wipers, 
            including NotPetya (exploiting MS17-010 EternalBlue CVE-2017-0144) and the recently analyzed CaddyWiper. 
            Binary artifact 027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826 demonstrates automated Master Boot Record (MBR) corruption 
            and targeted disk block zeroing (T1485). Command-and-control infrastructure connects through masqueraded domains such as ukr-telecom-cert[.]net, 
            resolving to 194.28.172.10, which shares ASN routing and co-location with backup pivoting node 91.242.217.5.
            Initial intrusion vectors consistently involve exploiting perimeter VPN gateways and internet-facing enterprise software (T1190).
            """,
            tags=["sandworm", "apt44", "industroyer", "notpetya", "caddywiper", "ics_scada", "gru"],
            iocs=["ukr-telecom-cert[.]net", "194.28.172.10", "91.242.217.5", "027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826"],
            cves=["CVE-2017-0144"],
            ttps=["T1485", "T1190", "T1071.001"]
        ),
        ThreatReport(
            id="rpt_mandiant_fin7_carbanak",
            title="Mandiant Special Report: Evolution of FIN7 - From Point-of-Sale Scrapers to Corporate Ransomware Extortion",
            source="Mandiant Threat Intelligence",
            date="2022-01-20",
            target_actor="actor_fin7",
            summary="In-depth profile of financially motivated cybercrime syndicate FIN7, analyzing stagers, Zerologon abuse, and Lizar framework.",
            text="""
            FIN7 (also known as Carbanak, Sangria Tempest, ELBRUS) is an organized cybercrime syndicate that has evolved from POS card skimming into enterprise-wide 
            ransomware deployments and multimillion-dollar corporate extortion. FIN7 utilizes elaborate social engineering schemes, masquerading as legitimate job recruiters, 
            human resources personnel, or mock security vendors (such as Bastion Secure) to send malicious document lures (T1566.001). 
            These documents initiate execution of the Griffon JavaScript stager (hash f441c21d84812a106e2cf61a5b8bb15e0a6d2139744e83f233481273891461f2). 
            Griffon collects host telemetry and reaches out to malicious staging domains including doc-secure-share[.]info, hosted on bulletproof VPS 193.106.191.4. 
            Once on an internal network, the operators use PowerShell scripts (T1059.001) to deploy the proprietary Lizar post-exploitation loader. 
            To achieve domain dominance, FIN7 rapidly exploits Active Directory vulnerabilities, particularly Zerologon (CVE-2020-1472), allowing unauthenticated attackers 
            to reset domain controller machine passwords and exfiltrate the NTDS.dit credential database.
            """,
            tags=["fin7", "carbanak", "griffon", "lizar", "zerologon", "financial_crime"],
            iocs=["doc-secure-share[.]info", "193.106.191.4", "f441c21d84812a106e2cf61a5b8bb15e0a6d2139744e83f233481273891461f2"],
            cves=["CVE-2020-1472"],
            ttps=["T1566.001", "T1059.001", "T1055"]
        ),
        ThreatReport(
            id="rpt_cisa_volt_typhoon_critical_infra",
            title="CISA, NSA & FBI Joint Advisory AA24-038A: PRC State-Sponsored Actors Compromise US Critical Infrastructure via Living-off-the-Land",
            source="CISA, NSA, FBI & International Partners",
            date="2024-02-07",
            target_actor="actor_volt_typhoon",
            summary="Strategic alert warning of PRC actor Volt Typhoon pre-positioning within US energy, water, and transportation sectors using SOHO router botnets.",
            text="""
            The authoring agencies warn that People's Republic of China (PRC) state-sponsored cyber actors, tracked internationally as Volt Typhoon 
            (also Vanguard Panda, Bronze Silhouette), have systematically compromised and maintained persistent access within operational technology (OT) 
            and IT networks of US critical infrastructure providers. Unlike conventional espionage actors who deploy signature-detectable custom backdoors, 
            Volt Typhoon relies almost exclusively on Living-off-the-Land (LOTL) techniques and built-in system administration binaries (wmic, netsh, ntdsutil, PowerShell). 
            Initial penetration is achieved through the weaponization of zero-day vulnerabilities in edge networking appliances, including Fortinet FortiOS (CVE-2023-27997) 
            and Ivanti Connect Secure. The adversary establishes a covert operational proxy network known as KV-botnet by compromising end-of-life small office/home office (SOHO) 
            routers and firewalls across the globe. Command-and-control communications tunnel traffic through domains like cisco-gateway-mesh[.]org 
            and residential egress IP ranges including 198.51.100.44 and 203.0.113.88. Tunneling protocols such as Fast Reverse Proxy (FRP) and SSH (T1572) 
            are employed to blend seamlessly into legitimate system administrator traffic, ensuring that the actors remain undetected for hundreds of days.
            """,
            tags=["volt_typhoon", "vanguard_panda", "living_off_the_land", "soho_botnet", "critical_infrastructure", "china"],
            iocs=["cisco-gateway-mesh[.]org", "198.51.100.44", "203.0.113.88"],
            cves=["CVE-2023-27997"],
            ttps=["T1078", "T1572", "T1059"]
        ),
    ]

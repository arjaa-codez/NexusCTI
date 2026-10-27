"""
Benchmark evaluation dataset for Cyber Threat Attribution.
Contains structured test scenarios with varying multi-hop reasoning depths.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class BenchmarkTestCase(BaseModel):
    id: str
    name: str
    query: str
    anchor_ioc: str
    ground_truth_actor: str
    expected_hops: int
    category: str  # 1_hop_direct, 2_hop_stager, 3_hop_infra_pivot, 4_hop_deep_chain, novel_telemetry
    description: str


def get_benchmark_dataset() -> List[BenchmarkTestCase]:
    """
    Returns 12 standardized CTI attribution test scenarios spanning 1-hop to 4-hop reasoning.
    """
    return [
        # --- 1-HOP / DIRECT CASES ---
        BenchmarkTestCase(
            id="test_case_01",
            name="APT29 SUNBURST Direct Backdoor Detection",
            query="Infected SolarWinds Orion build beaconing to primary C2 domain avsvmcloud[.]com with encoded DGA queries",
            anchor_ioc="avsvmcloud[.]com",
            ground_truth_actor="actor_apt29",
            expected_hops=2,
            category="1_hop_direct",
            description="Direct observation of primary SUNBURST C2 domain."
        ),
        BenchmarkTestCase(
            id="test_case_02",
            name="Sandworm Industroyer Power Grid Payload",
            query="ICS substation telemetry detecting CrashOverride Industroyer IEC-104 breaker manipulation payload",
            anchor_ioc="Industroyer (CrashOverride)",
            ground_truth_actor="actor_sandworm",
            expected_hops=1,
            category="1_hop_direct",
            description="Direct identification of proprietary Sandworm SCADA malware."
        ),
        BenchmarkTestCase(
            id="test_case_03",
            name="Lazarus AppleJeus Trojanized Installer",
            query="Cryptocurrency exchange employee downloaded fake DeFi wallet installer communicating with secure-crypto-wallet[.]org",
            anchor_ioc="secure-crypto-wallet[.]org",
            ground_truth_actor="actor_lazarus",
            expected_hops=2,
            category="1_hop_direct",
            description="Phishing application landing domain used in Lazarus cryptocurrency theft."
        ),

        # --- 2-HOP INTERMEDIARY CASES ---
        BenchmarkTestCase(
            id="test_case_04",
            name="APT28 Zebrocy Binary Hash to C2 Pivot",
            query="Endpoint detection flagged suspicious Delphi downloader binary hash a3d9e84b72110cfa2349e5d9c0281b37e221d604b1234f9a0c84112e31578e99 in temp folder",
            anchor_ioc="a3d9e84b72110cfa2349e5d9c0281b37e221d604b1234f9a0c84112e31578e99",
            ground_truth_actor="actor_apt28",
            expected_hops=2,
            category="2_hop_stager",
            description="Hash -> Zebrocy Malware -> APT28."
        ),
        BenchmarkTestCase(
            id="test_case_05",
            name="FIN7 Griffon Stager & Zerologon Exploitation",
            query="HR recruiting lure document dropped JavaScript payload hash f441c21d84812a106e2cf61a5b8bb15e0a6d2139744e83f233481273891461f2 targeting CVE-2020-1472",
            anchor_ioc="f441c21d84812a106e2cf61a5b8bb15e0a6d2139744e83f233481273891461f2",
            ground_truth_actor="actor_fin7",
            expected_hops=2,
            category="2_hop_stager",
            description="Stager hash -> Griffon -> FIN7."
        ),
        BenchmarkTestCase(
            id="test_case_06",
            name="Sandworm NotPetya Wiper Binary Artifact",
            query="Critical infrastructure file server MBR corrupted by disk zeroing wiper artifact 027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826",
            anchor_ioc="027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826",
            ground_truth_actor="actor_sandworm",
            expected_hops=2,
            category="2_hop_stager",
            description="Wiper artifact hash -> NotPetya -> Sandworm."
        ),

        # --- 3-HOP INFRASTRUCTURE PIVOT CASES ---
        BenchmarkTestCase(
            id="test_case_07",
            name="APT29 Multi-Hop Secondary Infrastructure Pivot",
            query="Egress firewall logged suspicious beaconing to isolated external IP address 185.225.17.42 with forged certificate serials",
            anchor_ioc="185.225.17.42",
            ground_truth_actor="actor_apt29",
            expected_hops=3,
            category="3_hop_infra_pivot",
            description="IP 185.225.17.42 -> resolves_from freescanonline[.]com -> shares_infra avsvmcloud[.]com -> SUNBURST -> APT29."
        ),
        BenchmarkTestCase(
            id="test_case_08",
            name="APT28 Shared DNS Resolution Pivot",
            query="DNS logging discovered host communicating with spoofed domain mail-update-service[.]net",
            anchor_ioc="mail-update-service[.]net",
            ground_truth_actor="actor_apt28",
            expected_hops=3,
            category="3_hop_infra_pivot",
            description="Domain mail-update-service -> IP 185.141.63.12 -> auth-microsoft365 -> Zebrocy -> APT28."
        ),
        BenchmarkTestCase(
            id="test_case_09",
            name="Volt Typhoon SOHO Mesh Egress Pivot",
            query="Perimeter gateway observed reverse tunneling session originating from residential IP 203.0.113.88 over Fast Reverse Proxy",
            anchor_ioc="203.0.113.88",
            ground_truth_actor="actor_volt_typhoon",
            expected_hops=3,
            category="3_hop_infra_pivot",
            description="IP 203.0.113.88 -> shares_infra 198.51.100.44 -> cisco-gateway-mesh[.]org -> KV-botnet -> Volt Typhoon."
        ),

        # --- 4-HOP DEEP RELATIONAL CHAIN CASES ---
        BenchmarkTestCase(
            id="test_case_10",
            name="Sandworm Obfuscated Subnet Pivot to BlackEnergy C2",
            query="Threat hunting discovered lateral movement traffic routing through dark subnet node 91.242.217.5 in European regional telecommunications segment",
            anchor_ioc="91.242.217.5",
            ground_truth_actor="actor_sandworm",
            expected_hops=4,
            category="4_hop_deep_chain",
            description="IP 91.242.217.5 -> shares_infra 194.28.172.10 -> ukr-telecom-cert[.]net -> BlackEnergy -> Sandworm."
        ),
        BenchmarkTestCase(
            id="test_case_11",
            name="Lazarus North Korean AS131279 Gateway Correlation",
            query="DeFi liquidation contract authorization initiated from North Korean border IP address 175.45.176.8",
            anchor_ioc="175.45.176.8",
            ground_truth_actor="actor_lazarus",
            expected_hops=3,
            category="4_hop_deep_chain",
            description="IP 175.45.176.8 -> resolves_from secure-crypto-wallet[.]org -> AppleJeus -> Lazarus."
        ),
        BenchmarkTestCase(
            id="test_case_12",
            name="FIN7 Hosting Staging Infrastructure Pivot",
            query="SIEM alert on suspicious outbound HTTPS connection to bulletproof hosting IP 193.106.191.4 carrying obfuscated payloads",
            anchor_ioc="193.106.191.4",
            ground_truth_actor="actor_fin7",
            expected_hops=3,
            category="4_hop_deep_chain",
            description="IP 193.106.191.4 -> resolves_from doc-secure-share[.]info -> Griffon -> FIN7."
        ),
    ]

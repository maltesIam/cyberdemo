"""
Unit tests for ConfidenceScoreCalculator.

Following TDD: These tests are written FIRST, before implementation.
The calculator scores alerts on a 0-100 scale across four weighted dimensions:
  - Intel (0-40): VirusTotal score, malware labels, source count
  - Behavior (0-30): MITRE technique risk, suspicious command lines
  - Context (0-20): CTEM risk level, asset criticality
  - Propagation (0-10): Number of affected hosts

Decision Thresholds:
  - Score >= 90: HIGH confidence - Auto-containment eligible
  - Score 50-89: MEDIUM confidence - Requires human approval
  - Score < 50: LOW confidence - Likely false positive
"""
import pytest

from src.services.confidence_score import (
    ConfidenceComponents,
    ConfidenceScoreCalculator,
    ThreatType,
    WeightProfile,
    WEIGHT_PROFILES,
    THRESHOLD_HIGH_CONFIDENCE,
    THRESHOLD_MEDIUM_CONFIDENCE,
    calculate_confidence_score,
    calculate_intel_component,
    calculate_behavior_component,
    calculate_context_component,
    calculate_propagation_component,
)


class TestConfidenceComponents:
    """Tests for the ConfidenceComponents dataclass."""

    def test_components_default_to_zero(self):
        """All component scores default to zero."""
        components = ConfidenceComponents()
        assert components.intel == 0
        assert components.behavior == 0
        assert components.context == 0
        assert components.propagation == 0

    def test_components_store_values(self):
        """Components store the values they are created with."""
        components = ConfidenceComponents(
            intel=30, behavior=20, context=15, propagation=5
        )
        assert components.intel == 30
        assert components.behavior == 20
        assert components.context == 15
        assert components.propagation == 5

    def test_components_total(self):
        """Total is the sum of all component scores."""
        components = ConfidenceComponents(
            intel=30, behavior=20, context=15, propagation=5
        )
        assert components.total == 70

    def test_components_total_all_zero(self):
        """Total is zero when all components are zero."""
        components = ConfidenceComponents()
        assert components.total == 0

    def test_components_total_all_max(self):
        """Total is 100 when all components are at maximum."""
        components = ConfidenceComponents(
            intel=40, behavior=30, context=20, propagation=10
        )
        assert components.total == 100


class TestWeightProfile:
    """Tests for the WeightProfile configuration."""

    def test_default_weights_sum_to_100(self):
        """Default weight profile sums to 100."""
        profile = WeightProfile()
        total = profile.intel + profile.behavior + profile.context + profile.propagation
        assert total == 100

    def test_custom_weights_must_sum_to_100(self):
        """Custom weights that don't sum to 100 raise ValueError."""
        with pytest.raises(ValueError, match="Weights must sum to 100"):
            WeightProfile(intel=50, behavior=30, context=20, propagation=5)

    def test_valid_custom_weights(self):
        """Valid custom weights are accepted."""
        profile = WeightProfile(intel=25, behavior=35, context=25, propagation=15)
        assert profile.intel == 25
        assert profile.behavior == 35
        assert profile.context == 25
        assert profile.propagation == 15

    def test_all_threat_type_profiles_sum_to_100(self):
        """All predefined threat type profiles sum to 100."""
        for threat_type, profile in WEIGHT_PROFILES.items():
            total = profile.intel + profile.behavior + profile.context + profile.propagation
            assert total == 100, f"{threat_type} profile does not sum to 100"


class TestThreatTypeProfiles:
    """Tests for threat type weight profile selection."""

    def test_default_profile_exists(self):
        """DEFAULT threat type has a weight profile."""
        assert ThreatType.DEFAULT in WEIGHT_PROFILES

    def test_ransomware_profile_prioritizes_behavior(self):
        """RANSOMWARE profile gives higher weight to behavior."""
        profile = WEIGHT_PROFILES[ThreatType.RANSOMWARE]
        assert profile.behavior > profile.intel

    def test_lateral_movement_profile_prioritizes_propagation(self):
        """LATERAL_MOVEMENT profile gives higher weight to propagation."""
        profile = WEIGHT_PROFILES[ThreatType.LATERAL_MOVEMENT]
        assert profile.propagation >= 30

    def test_malware_profile_prioritizes_intel(self):
        """MALWARE profile gives highest weight to intel."""
        profile = WEIGHT_PROFILES[ThreatType.MALWARE]
        assert profile.intel > profile.behavior
        assert profile.intel > profile.context
        assert profile.intel > profile.propagation


class TestCalculateIntel:
    """Tests for the intel scoring dimension (0-40 points)."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceScoreCalculator()

    def test_high_vt_score_gives_30_points(self, calculator):
        """VT score > 50/74 yields +30 points."""
        score = calculator._calculate_intel(vt_score=55, vt_total=74, malware_labels=[])
        assert score == 30

    def test_high_vt_score_with_malware_labels_gives_40(self, calculator):
        """VT score > 50/74 with known malware labels yields 30 + 10 = 40."""
        score = calculator._calculate_intel(
            vt_score=55, vt_total=74, malware_labels=["trojan"]
        )
        assert score == 40

    def test_malware_labels_only_gives_10(self, calculator):
        """Known malware labels without high VT score yields +10."""
        score = calculator._calculate_intel(vt_score=20, vt_total=74, malware_labels=["ransomware"])
        assert score == 10

    def test_no_detections_gives_zero(self, calculator):
        """No VT detections and no labels yields 0 points."""
        score = calculator._calculate_intel(vt_score=0, vt_total=74, malware_labels=[])
        assert score == 0

    def test_vt_score_exactly_50_not_above(self, calculator):
        """VT score of exactly 50/74 does NOT meet the > 50 threshold."""
        score = calculator._calculate_intel(vt_score=50, vt_total=74, malware_labels=[])
        assert score == 0

    def test_vt_score_51_meets_threshold(self, calculator):
        """VT score of 51/74 meets the > 50 threshold."""
        score = calculator._calculate_intel(vt_score=51, vt_total=74, malware_labels=[])
        assert score == 30

    def test_multiple_malware_labels_still_10(self, calculator):
        """Multiple malware labels still yield only 10 points (not additive)."""
        score = calculator._calculate_intel(
            vt_score=0, vt_total=74, malware_labels=["trojan", "apt", "backdoor"]
        )
        assert score == 10

    def test_empty_malware_labels_no_bonus(self, calculator):
        """Empty malware_labels list gives no label bonus."""
        score = calculator._calculate_intel(vt_score=0, vt_total=74, malware_labels=[])
        assert score == 0

    def test_never_exceeds_40(self, calculator):
        """Intel score never exceeds the 40-point cap."""
        score = calculator._calculate_intel(
            vt_score=74, vt_total=74, malware_labels=["trojan", "ransomware"]
        )
        assert score <= 40

    def test_source_count_bonus_at_3_sources(self, calculator):
        """3+ intel sources add a +5 bonus."""
        score = calculator._calculate_intel(
            vt_score=0, vt_total=74, malware_labels=[], source_count=3
        )
        assert score == 5

    def test_source_count_bonus_stacks_with_labels(self, calculator):
        """Source count bonus stacks with malware labels."""
        score = calculator._calculate_intel(
            vt_score=0, vt_total=74, malware_labels=["trojan"], source_count=3
        )
        assert score == 15  # 10 (label) + 5 (sources)

    def test_source_count_bonus_capped_at_40(self, calculator):
        """Even with all bonuses, intel score is capped at 40."""
        score = calculator._calculate_intel(
            vt_score=55, vt_total=74, malware_labels=["trojan"], source_count=5
        )
        assert score == 40  # 30 (VT) + 10 (label) + 5 (sources) = 45, capped to 40


class TestCalculateBehavior:
    """Tests for the behavior scoring dimension (0-30 points)."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceScoreCalculator()

    def test_high_risk_mitre_gives_20(self, calculator):
        """A high-risk MITRE technique yields +20 points."""
        score = calculator._calculate_behavior(
            mitre_technique="T1003.001", cmdline="normal.exe"
        )
        assert score == 20

    def test_suspicious_cmdline_encoded_powershell_gives_10(self, calculator):
        """Encoded PowerShell in cmdline yields +10 points."""
        score = calculator._calculate_behavior(
            mitre_technique="T9999",  # Unknown technique to isolate cmdline scoring
            cmdline="powershell.exe -EncodedCommand SGVsbG8gV29ybGQ="
        )
        assert score == 10

    def test_suspicious_cmdline_mimikatz_gives_10(self, calculator):
        """Mimikatz in cmdline yields +10 points."""
        score = calculator._calculate_behavior(
            mitre_technique="T9999",  # Unknown technique to isolate cmdline scoring
            cmdline='mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit'
        )
        assert score == 10

    def test_high_risk_technique_plus_suspicious_cmdline_gives_30(self, calculator):
        """High-risk technique + suspicious cmdline = 20 + 10 = 30."""
        score = calculator._calculate_behavior(
            mitre_technique="T1003.001",
            cmdline='mimikatz.exe "privilege::debug" exit'
        )
        assert score == 30

    def test_legitimate_process_gives_zero(self, calculator):
        """Non-risky technique with clean cmdline yields 0."""
        score = calculator._calculate_behavior(
            mitre_technique="T1083", cmdline="explorer.exe"
        )
        # T1083 is now medium risk, so it gives 10, but still within spec
        # since "legitimate" should mean non-suspicious technique
        score = calculator._calculate_behavior(
            mitre_technique="T9999", cmdline="explorer.exe"
        )
        assert score == 0

    def test_unknown_technique_gives_zero_technique_score(self, calculator):
        """Unknown MITRE technique yields 0 technique points."""
        score = calculator._calculate_behavior(
            mitre_technique="T9999.999", cmdline="explorer.exe"
        )
        assert score == 0

    def test_empty_cmdline_no_cmdline_bonus(self, calculator):
        """Empty cmdline yields no cmdline bonus."""
        score = calculator._calculate_behavior(mitre_technique="T1003.001", cmdline="")
        assert score == 20

    def test_never_exceeds_30(self, calculator):
        """Behavior score never exceeds the 30-point cap."""
        score = calculator._calculate_behavior(
            mitre_technique="T1003.001",
            cmdline='powershell.exe -EncodedCommand mimikatz.exe'
        )
        assert score <= 30

    def test_case_insensitive_cmdline_check(self, calculator):
        """Cmdline check is case-insensitive."""
        score = calculator._calculate_behavior(
            mitre_technique="T9999",
            cmdline="POWERSHELL.EXE -ENCODEDCOMMAND abc123"
        )
        assert score == 10

    def test_medium_risk_technique_gives_10(self, calculator):
        """Medium-risk MITRE technique yields +10 points."""
        score = calculator._calculate_behavior(
            mitre_technique="T1083", cmdline="explorer.exe"
        )
        assert score == 10

    def test_high_risk_takes_precedence_over_medium(self, calculator):
        """High-risk technique score is used, not added to medium-risk."""
        # If we somehow had both (impossible), high-risk wins
        score = calculator._calculate_behavior(
            mitre_technique="T1003.001", cmdline="explorer.exe"
        )
        assert score == 20  # Not 30


class TestCalculateContext:
    """Tests for the context scoring dimension (0-20 points)."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceScoreCalculator()

    def test_red_risk_gives_15(self, calculator):
        """Host with Red CTEM risk yields +15 points."""
        score = calculator._calculate_context(ctem_risk="Red", asset_criticality="low")
        assert score == 15

    def test_vip_criticality_gives_5(self, calculator):
        """VIP asset criticality yields +5 points."""
        score = calculator._calculate_context(ctem_risk="Green", asset_criticality="vip")
        assert score == 5

    def test_red_risk_plus_vip_gives_20(self, calculator):
        """Red risk + VIP criticality = 15 + 5 = 20."""
        score = calculator._calculate_context(ctem_risk="Red", asset_criticality="vip")
        assert score == 20

    def test_green_risk_low_criticality_gives_zero(self, calculator):
        """Green risk with low criticality yields 0."""
        score = calculator._calculate_context(ctem_risk="Green", asset_criticality="low")
        assert score == 0

    def test_yellow_risk_gives_zero(self, calculator):
        """Yellow CTEM risk yields 0 points (only Red triggers score)."""
        score = calculator._calculate_context(ctem_risk="Yellow", asset_criticality="low")
        assert score == 0

    def test_critical_criticality_gives_5(self, calculator):
        """Critical asset criticality also yields +5 (same as VIP)."""
        score = calculator._calculate_context(ctem_risk="Green", asset_criticality="critical")
        assert score == 5

    def test_never_exceeds_20(self, calculator):
        """Context score never exceeds the 20-point cap."""
        score = calculator._calculate_context(ctem_risk="Red", asset_criticality="vip")
        assert score <= 20


class TestCalculatePropagation:
    """Tests for the propagation scoring dimension (0-10 points)."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceScoreCalculator()

    def test_one_host_gives_2(self, calculator):
        """1 affected host yields +2 points."""
        score = calculator._calculate_propagation(affected_hosts=1)
        assert score == 2

    def test_two_hosts_gives_5(self, calculator):
        """2 affected hosts yields +5 points."""
        score = calculator._calculate_propagation(affected_hosts=2)
        assert score == 5

    def test_five_hosts_gives_5(self, calculator):
        """5 affected hosts yields +5 points (still in 2-5 range)."""
        score = calculator._calculate_propagation(affected_hosts=5)
        assert score == 5

    def test_six_hosts_gives_10(self, calculator):
        """6 affected hosts yields +10 points."""
        score = calculator._calculate_propagation(affected_hosts=6)
        assert score == 10

    def test_zero_hosts_gives_zero(self, calculator):
        """0 affected hosts yields 0 points."""
        score = calculator._calculate_propagation(affected_hosts=0)
        assert score == 0

    def test_large_number_gives_10(self, calculator):
        """Very large host count still yields 10 (capped)."""
        score = calculator._calculate_propagation(affected_hosts=500)
        assert score == 10

    def test_never_exceeds_10(self, calculator):
        """Propagation score never exceeds the 10-point cap."""
        score = calculator._calculate_propagation(affected_hosts=1000)
        assert score <= 10


class TestCalculate:
    """Tests for the main calculate() method that combines all dimensions."""

    @pytest.fixture
    def calculator(self):
        return ConfidenceScoreCalculator()

    def test_returns_total_and_components(self, calculator):
        """calculate() returns both total score and component breakdown."""
        total, components = calculator.calculate(
            vt_score=55, vt_total=74, malware_labels=["trojan"],
            mitre_technique="T1003.001", cmdline='mimikatz.exe exit',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=6
        )
        assert isinstance(total, int)
        assert isinstance(components, ConfidenceComponents)

    def test_maximum_score_is_100(self, calculator):
        """Maximum possible score is 100."""
        total, components = calculator.calculate(
            vt_score=55, vt_total=74, malware_labels=["trojan"],
            mitre_technique="T1003.001", cmdline='mimikatz.exe exit',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=6
        )
        assert total == 100
        assert components.total == 100

    def test_minimum_score_is_zero(self, calculator):
        """Minimum possible score is 0."""
        total, components = calculator.calculate(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="T9999", cmdline="explorer.exe",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=0
        )
        assert total == 0
        assert components.total == 0

    def test_components_breakdown_matches_total(self, calculator):
        """The sum of individual components equals the total."""
        total, components = calculator.calculate(
            vt_score=55, vt_total=74, malware_labels=[],
            mitre_technique="T1003.001", cmdline="normal.exe",
            ctem_risk="Red", asset_criticality="low",
            affected_hosts=3
        )
        expected = components.intel + components.behavior + components.context + components.propagation
        assert total == expected
        assert total == components.total

    def test_score_clamped_between_0_and_100(self, calculator):
        """Total score is always clamped between 0 and 100."""
        total, _ = calculator.calculate(
            vt_score=74, vt_total=74, malware_labels=["trojan", "apt"],
            mitre_technique="T1003.001",
            cmdline='powershell.exe -EncodedCommand mimikatz.exe',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=100
        )
        assert 0 <= total <= 100

    def test_scenario_high_confidence_malware(self, calculator):
        """Scenario: Clear malware on vulnerable VIP host with propagation."""
        total, components = calculator.calculate(
            vt_score=60, vt_total=74, malware_labels=["ransomware"],
            mitre_technique="T1486", cmdline='powershell.exe -EncodedCommand abc',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=8
        )
        # Intel: 30 (VT > 50) + 10 (label) = 40
        assert components.intel == 40
        # Behavior: 20 (T1486 high risk) + 10 (encoded PS) = 30
        assert components.behavior == 30
        # Context: 15 (Red) + 5 (VIP) = 20
        assert components.context == 20
        # Propagation: 10 (8 >= 6)
        assert components.propagation == 10
        assert total == 100

    def test_scenario_low_confidence_benign(self, calculator):
        """Scenario: Benign process on clean host, no propagation."""
        total, components = calculator.calculate(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="T9999", cmdline="notepad.exe C:\\readme.txt",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=0
        )
        assert components.intel == 0
        assert components.behavior == 0
        assert components.context == 0
        assert components.propagation == 0
        assert total == 0

    def test_scenario_medium_confidence_suspicious(self, calculator):
        """Scenario: Some VT hits, suspicious cmdline, moderate context."""
        total, components = calculator.calculate(
            vt_score=30, vt_total=74, malware_labels=["downloader"],
            mitre_technique="T1059.001",
            cmdline='powershell.exe -EncodedCommand base64stuff',
            ctem_risk="Red", asset_criticality="low",
            affected_hosts=1
        )
        # Intel: 0 (VT <= 50) + 10 (label) = 10
        assert components.intel == 10
        # Behavior: 20 (T1059.001 high risk) + 10 (encoded PS) = 30
        assert components.behavior == 30
        # Context: 15 (Red) + 0 (low) = 15
        assert components.context == 15
        # Propagation: 2 (1 host)
        assert components.propagation == 2
        assert total == 57

    def test_default_parameters(self, calculator):
        """calculate() works with all default/empty values."""
        total, components = calculator.calculate(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="", cmdline="",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=0
        )
        assert total == 0
        assert components.total == 0

    def test_source_count_parameter(self, calculator):
        """calculate() accepts and uses source_count parameter."""
        total, components = calculator.calculate(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="", cmdline="",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=0,
            source_count=3
        )
        assert components.intel == 5  # +5 for 3+ sources


class TestCalculateWeighted:
    """Tests for the calculate_weighted() method with threat-type profiles."""

    def test_weighted_with_ransomware_profile(self):
        """Weighted calculation uses ransomware profile when specified."""
        calculator = ConfidenceScoreCalculator(threat_type=ThreatType.RANSOMWARE)
        total, components = calculator.calculate_weighted(
            vt_score=55, vt_total=74, malware_labels=["ransomware"],
            mitre_technique="T1486", cmdline='mimikatz.exe',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=6
        )
        assert 0 <= total <= 100
        # With ransomware profile, behavior is weighted 40% instead of 30%
        # All components are at max, so weighted total should be 100
        assert total == 100

    def test_weighted_with_lateral_movement_profile(self):
        """Lateral movement profile gives more weight to propagation."""
        calc_default = ConfidenceScoreCalculator(threat_type=ThreatType.DEFAULT)
        calc_lateral = ConfidenceScoreCalculator(threat_type=ThreatType.LATERAL_MOVEMENT)

        # Scenario with high propagation but lower other scores
        total_default, _ = calc_default.calculate_weighted(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="T1021.002", cmdline="psexec.exe",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=10
        )
        total_lateral, _ = calc_lateral.calculate_weighted(
            vt_score=0, vt_total=74, malware_labels=[],
            mitre_technique="T1021.002", cmdline="psexec.exe",
            ctem_risk="Green", asset_criticality="low",
            affected_hosts=10
        )

        # Lateral movement profile should give higher score due to propagation weight
        assert total_lateral > total_default

    def test_weighted_with_custom_weights(self):
        """Calculator accepts custom weight profile."""
        custom_weights = WeightProfile(intel=50, behavior=20, context=20, propagation=10)
        calculator = ConfidenceScoreCalculator(weights=custom_weights)

        total, _ = calculator.calculate_weighted(
            vt_score=55, vt_total=74, malware_labels=["trojan"],
            mitre_technique="T1003.001", cmdline='mimikatz.exe',
            ctem_risk="Red", asset_criticality="vip",
            affected_hosts=6
        )
        assert 0 <= total <= 100

    def test_weighted_custom_overrides_threat_type(self):
        """Custom weights override threat_type selection."""
        custom_weights = WeightProfile(intel=10, behavior=10, context=10, propagation=70)
        calculator = ConfidenceScoreCalculator(
            threat_type=ThreatType.RANSOMWARE,
            weights=custom_weights
        )

        assert calculator.weights.propagation == 70  # Custom, not ransomware profile


class TestConvenienceFunctions:
    """Tests for the module-level convenience functions."""

    def test_calculate_confidence_score_returns_tuple(self):
        """calculate_confidence_score returns (score, components, decision)."""
        result = calculate_confidence_score(
            detection={"mitre_technique": "T1003.001", "cmdline": "mimikatz.exe"},
            intel={"vt_score": 60, "vt_total": 74, "labels": ["trojan"], "sources": 3},
            ctem={"risk_color": "Red", "criticality": "vip"},
            propagation={"affected_hosts": 6}
        )
        assert len(result) == 3
        score, components, decision = result
        assert isinstance(score, int)
        assert isinstance(components, ConfidenceComponents)
        assert decision in ("AUTO_CONTAIN", "REQUIRES_APPROVAL", "FALSE_POSITIVE")

    def test_calculate_confidence_score_auto_contain_decision(self):
        """High score results in AUTO_CONTAIN decision."""
        score, _, decision = calculate_confidence_score(
            detection={"mitre_technique": "T1003.001", "cmdline": "mimikatz.exe"},
            intel={"vt_score": 60, "vt_total": 74, "labels": ["trojan"]},
            ctem={"risk_color": "Red", "criticality": "vip"},
            propagation={"affected_hosts": 10}
        )
        assert score >= THRESHOLD_HIGH_CONFIDENCE
        assert decision == "AUTO_CONTAIN"

    def test_calculate_confidence_score_requires_approval_decision(self):
        """Medium score results in REQUIRES_APPROVAL decision."""
        score, _, decision = calculate_confidence_score(
            detection={"mitre_technique": "T1059.001", "cmdline": "powershell.exe -EncodedCommand abc"},
            intel={"vt_score": 30, "vt_total": 74, "labels": ["downloader"]},
            ctem={"risk_color": "Red", "criticality": "low"},
            propagation={"affected_hosts": 1}
        )
        # Intel: 10 (label), Behavior: 30 (20 technique + 10 cmdline), Context: 15 (Red), Propagation: 2 = 57
        assert THRESHOLD_MEDIUM_CONFIDENCE <= score < THRESHOLD_HIGH_CONFIDENCE
        assert decision == "REQUIRES_APPROVAL"

    def test_calculate_confidence_score_false_positive_decision(self):
        """Low score results in FALSE_POSITIVE decision."""
        score, _, decision = calculate_confidence_score(
            detection={"mitre_technique": "T9999", "cmdline": "notepad.exe"},
            intel={"vt_score": 0, "vt_total": 74, "labels": []},
            ctem={"risk_color": "Green", "criticality": "low"},
            propagation={"affected_hosts": 0}
        )
        assert score < THRESHOLD_MEDIUM_CONFIDENCE
        assert decision == "FALSE_POSITIVE"

    def test_calculate_intel_component_function(self):
        """calculate_intel_component returns correct intel score."""
        score = calculate_intel_component({
            "vt_score": 55,
            "vt_total": 74,
            "labels": ["trojan"],
            "sources": 3
        })
        assert score == 40  # 30 (VT) + 10 (label) = 40 (capped)

    def test_calculate_behavior_component_function(self):
        """calculate_behavior_component returns correct behavior score."""
        score = calculate_behavior_component({
            "mitre_technique": "T1003.001",
            "cmdline": "mimikatz.exe"
        })
        assert score == 30  # 20 (technique) + 10 (cmdline)

    def test_calculate_context_component_function(self):
        """calculate_context_component returns correct context score."""
        score = calculate_context_component({
            "risk_color": "Red",
            "criticality": "vip"
        })
        assert score == 20  # 15 (Red) + 5 (VIP)

    def test_calculate_propagation_component_function(self):
        """calculate_propagation_component returns correct propagation score."""
        score = calculate_propagation_component({"affected_hosts": 6})
        assert score == 10  # 6+ hosts

    def test_convenience_functions_handle_alternate_keys(self):
        """Convenience functions handle both key naming conventions."""
        intel_score = calculate_intel_component({
            "vt_score": 55,
            "malware_labels": ["trojan"],
            "source_count": 3
        })
        assert intel_score == 40

        context_score = calculate_context_component({
            "ctem_risk": "Red",
            "asset_criticality": "vip"
        })
        assert context_score == 20

    def test_calculate_confidence_score_with_threat_type(self):
        """calculate_confidence_score accepts threat_type parameter."""
        score, _, decision = calculate_confidence_score(
            detection={"mitre_technique": "T1486", "cmdline": "vssadmin delete"},
            intel={"vt_score": 60, "labels": ["ransomware"]},
            ctem={"risk_color": "Red", "criticality": "critical"},
            propagation={"affected_hosts": 10},
            threat_type=ThreatType.RANSOMWARE
        )
        assert isinstance(score, int)
        assert decision in ("AUTO_CONTAIN", "REQUIRES_APPROVAL", "FALSE_POSITIVE")


class TestThresholdConstants:
    """Tests for threshold constant values."""

    def test_high_confidence_threshold_is_90(self):
        """HIGH confidence threshold is 90."""
        assert THRESHOLD_HIGH_CONFIDENCE == 90

    def test_medium_confidence_threshold_is_50(self):
        """MEDIUM confidence threshold is 50."""
        assert THRESHOLD_MEDIUM_CONFIDENCE == 50

    def test_thresholds_are_ordered(self):
        """Thresholds are correctly ordered."""
        assert THRESHOLD_MEDIUM_CONFIDENCE < THRESHOLD_HIGH_CONFIDENCE

from __future__ import annotations

from backend.app.config import Settings, get_settings


def test_settings_initialization():
    settings = Settings()
    assert settings.app_name == "FraudGraph Agent"
    assert settings.agent_max_steps >= 1
    assert settings.risk_low_threshold < settings.risk_medium_threshold < settings.risk_high_threshold


def test_settings_properties():
    settings = Settings()
    # Unconfigured TigerGraph by default
    assert not settings.tigergraph_configured or (settings.tigergraph_host != "")
    assert not settings.allow_action_execution


def test_get_settings_cached():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

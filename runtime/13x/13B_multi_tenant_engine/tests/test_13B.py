"""Tests for STARCORE 13B Multi-Tenant Engine"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "13B"


def test_tenant_registration() -> None:
    from tenant_engine import MultiTenantEngine, TenantConfig
    engine = MultiTenantEngine()
    cfg = TenantConfig(name="Acme Corp", tier="enterprise")
    engine.register_tenant(cfg)
    assert engine._tenants[cfg.tenant_id].name == "Acme Corp"


def test_feature_flags() -> None:
    from tenant_engine import MultiTenantEngine, TenantConfig
    engine = MultiTenantEngine()
    cfg = TenantConfig(name="Beta", feature_flags={"ai_analytics": True, "export": False})
    engine.register_tenant(cfg)
    assert engine.is_feature_enabled(cfg.tenant_id, "ai_analytics") is True
    assert engine.is_feature_enabled(cfg.tenant_id, "export") is False


def test_quota_enforcement() -> None:
    from tenant_engine import MultiTenantEngine, TenantConfig
    engine = MultiTenantEngine()
    cfg = TenantConfig(name="Limited", resource_limits={"api_calls": 1000.0})
    engine.register_tenant(cfg)
    assert engine.check_quota(cfg.tenant_id, "api_calls", 500) is True
    assert engine.check_quota(cfg.tenant_id, "api_calls", 1500) is False

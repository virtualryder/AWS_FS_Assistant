"""
Build validation tests for AWS Financial Services Assistant.

Tests:
  1. All new/modified agent files pass syntax and import checks
  2. Config values are correct
  3. AWS doc URL structure is valid
  4. Agent system prompts contain required regulation sections
  5. FinServChatAgent interface matches what app.py expects
  6. Discovery agent structure is correct
  7. Regulation accuracy spot-checks

Run with: python -m pytest tests/test_build_validation.py -v
"""

import ast
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Syntax validation
# ─────────────────────────────────────────────────────────────────────────────

FILES_TO_CHECK = [
    "agent/aws_architect_agent.py",
    "agent/genai_ml_agent.py",
    "agent/chat_agent.py",
    "agent/discovery_agent.py",
    "scraper/aws_doc_urls.py",
    "config.py",
    "app.py",
]


def _parse_file(rel_path: str) -> ast.Module:
    p = ROOT / rel_path
    source = p.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(p))


def test_syntax_aws_architect_agent():
    _parse_file("agent/aws_architect_agent.py")


def test_syntax_genai_ml_agent():
    _parse_file("agent/genai_ml_agent.py")


def test_syntax_chat_agent():
    _parse_file("agent/chat_agent.py")


def test_syntax_discovery_agent():
    _parse_file("agent/discovery_agent.py")


def test_syntax_doc_urls():
    _parse_file("scraper/aws_doc_urls.py")


def test_syntax_config():
    _parse_file("config.py")


def test_syntax_app():
    _parse_file("app.py")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Config validation
# ─────────────────────────────────────────────────────────────────────────────

def test_config_app_name():
    from config import APP_NAME
    assert "Financial Services" in APP_NAME, f"Expected 'Financial Services' in APP_NAME, got: {APP_NAME}"


def test_config_model():
    from config import MODEL_NAME
    assert MODEL_NAME == "claude-sonnet-4-6", f"Unexpected model: {MODEL_NAME}"


def test_config_top_k_increased():
    """Financial services needs more context — TOP_K should be >= 10."""
    from config import TOP_K
    assert TOP_K >= 10, f"TOP_K should be >= 10 for financial services context, got {TOP_K}"


def test_config_collection_name():
    """Collection name should indicate financial services."""
    from config import COLLECTION_NAME
    assert "finserv" in COLLECTION_NAME or "fin" in COLLECTION_NAME, \
        f"Collection name should indicate financial services, got: {COLLECTION_NAME}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. AWS doc URLs validation
# ─────────────────────────────────────────────────────────────────────────────

def test_doc_urls_financial_services_services_present():
    """Critical financial services security/compliance services must be in SEED_URLS."""
    from scraper.aws_doc_urls import SEED_URLS
    required = ["macie", "audit_manager", "kms", "cloudtrail", "config", "securityhub", "backup"]
    for key in required:
        assert key in SEED_URLS, f"Missing financial services key: {key}"


def test_doc_urls_ai_services_present():
    """AI services must be present for GenAI/ML agent grounding."""
    from scraper.aws_doc_urls import SEED_URLS
    required = ["bedrock", "bedrock_agentcore", "sagemaker", "a2i"]
    for key in required:
        assert key in SEED_URLS, f"Missing AI service key: {key}"


def test_doc_urls_all_have_required_fields():
    from scraper.aws_doc_urls import SEED_URLS
    for key, info in SEED_URLS.items():
        assert "name" in info, f"Missing 'name' in SEED_URLS['{key}']"
        assert "url" in info, f"Missing 'url' in SEED_URLS['{key}']"
        assert "source_label" in info, f"Missing 'source_label' in SEED_URLS['{key}']"
        assert "tier" in info, f"Missing 'tier' in SEED_URLS['{key}']"
        assert info["tier"] in (1, 2, 3), f"Invalid tier {info['tier']} in SEED_URLS['{key}']"


def test_doc_urls_primary_keys_exist_in_seed_urls():
    from scraper.aws_doc_urls import SEED_URLS, PRIMARY_SEED_KEYS
    for key in PRIMARY_SEED_KEYS:
        assert key in SEED_URLS, f"PRIMARY_SEED_KEYS contains '{key}' not in SEED_URLS"


def test_doc_urls_optional_keys_exist_in_seed_urls():
    from scraper.aws_doc_urls import SEED_URLS, OPTIONAL_SEED_KEYS
    for key in OPTIONAL_SEED_KEYS:
        assert key in SEED_URLS, f"OPTIONAL_SEED_KEYS contains '{key}' not in SEED_URLS"


def test_doc_urls_no_duplicates_across_groups():
    from scraper.aws_doc_urls import PRIMARY_SEED_KEYS, OPTIONAL_SEED_KEYS
    overlap = set(PRIMARY_SEED_KEYS) & set(OPTIONAL_SEED_KEYS)
    assert not overlap, f"Keys in both PRIMARY and OPTIONAL: {overlap}"


def test_doc_urls_financial_services_topic_keyword():
    """Financial services specific keywords must be in the topic map."""
    from scraper.aws_doc_urls import TOPIC_KEYWORD_MAP
    finserv_keywords = ["pci dss", "glba", "sox", "ffiec", "compliance", "fraud detection", "aml"]
    for kw in finserv_keywords:
        assert kw in TOPIC_KEYWORD_MAP, f"Missing financial services topic keyword: '{kw}'"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Regulation accuracy — spot-check system prompts
# ─────────────────────────────────────────────────────────────────────────────

def _read_agent_source(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_glba_2023_requirements_in_architect_agent():
    """GLBA 2023 key requirements must appear in the AWS Architect agent system prompt."""
    source = _read_agent_source("agent/aws_architect_agent.py")
    required_terms = [
        "AES-256",           # encryption standard
        "TLS 1.2",           # transit encryption
        "MFA",               # multi-factor auth
        "30 calendar days",  # FTC breach notification timeline
        "500",               # breach notification threshold
        "2023",              # amendment year
        "Safeguards Rule",   # proper name
    ]
    for term in required_terms:
        assert term in source, f"GLBA 2023 term '{term}' missing from AWS Architect agent"


def test_pci_dss_v401_in_architect_agent():
    """PCI DSS v4.0.1 requirements must appear in the AWS Architect agent."""
    source = _read_agent_source("agent/aws_architect_agent.py")
    required_terms = [
        "v4.0.1",
        "March 31, 2025",    # mandatory date
        "12 character",      # password minimum
        "field-level",       # encryption requirement (disk-level no longer sufficient)
        "automated",         # SIEM requirement for log review
        "DMARC",             # email security
    ]
    for term in required_terms:
        assert term in source, f"PCI DSS v4.0.1 term '{term}' missing from AWS Architect agent"


def test_sox_itgc_categories_in_architect_agent():
    """SOX 404 ITGC categories must be in the AWS Architect agent (case-insensitive)."""
    source = _read_agent_source("agent/aws_architect_agent.py").lower()
    itgc_categories = [
        "access management",
        "change management",
        "computer operations",
        "as 2201",
    ]
    for term in itgc_categories:
        assert term in source, f"SOX ITGC term '{term}' missing from AWS Architect agent"


def test_ffiec_booklets_referenced():
    """FFIEC booklets (AIO, DA&M) must be referenced in the AWS Architect agent."""
    source = _read_agent_source("agent/aws_architect_agent.py")
    assert "AIO" in source or "Architecture, Infrastructure" in source, \
        "FFIEC AIO booklet not referenced"
    assert "DA&M" in source or "2024" in source, \
        "FFIEC DA&M (Aug 2024) booklet not referenced"


def test_mrm_guidance_supersedes_sr117():
    """MRM guidance (April 2026) superseding SR 11-7 must be noted."""
    source = _read_agent_source("agent/aws_architect_agent.py")
    assert "SR 11-7" in source or "supersedes" in source.lower(), \
        "Interagency MRM Guidance (Apr 2026) not mentioned"
    assert "2026" in source, "April 2026 MRM guidance year not mentioned"
    # Critical: Gen AI exclusion must be noted
    assert "EXCLUDED" in source or "excluded" in source, \
        "Gen AI exclusion from MRM guidance not mentioned"


def test_nist_ai_rmf_in_genai_agent():
    """NIST AI RMF must appear in the GenAI/ML agent."""
    source = _read_agent_source("agent/genai_ml_agent.py")
    assert "NIST AI RMF" in source, "NIST AI RMF not in GenAI/ML agent"
    assert "AI 600-1" in source, "NIST AI 600-1 (GenAI Profile, Jul 2024) not referenced"
    assert "GOVERN" in source, "NIST AI RMF GOVERN function not mentioned"
    assert "confabulation" in source.lower() or "Confabulation" in source, \
        "Confabulation (key GenAI risk) not addressed"


def test_genai_agent_covers_fair_lending():
    """Fair lending (ECOA) bias obligations must be in GenAI agent."""
    source = _read_agent_source("agent/genai_ml_agent.py")
    assert "ECOA" in source or "Fair" in source, \
        "Fair lending (ECOA) not mentioned in GenAI/ML agent"
    assert "bias" in source.lower(), "Bias testing not mentioned in GenAI/ML agent"


def test_genai_agent_mrm_exclusion_noted():
    """Gen AI exclusion from April 2026 MRM guidance must be noted in GenAI agent."""
    source = _read_agent_source("agent/genai_ml_agent.py")
    assert "excluded" in source.lower() or "EXCLUDED" in source, \
        "Gen AI exclusion from 2026 MRM guidance not noted in GenAI agent"
    assert "RFI" in source, "Pending RFI for Gen AI governance not mentioned"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Chat agent orchestrator interface
# ─────────────────────────────────────────────────────────────────────────────

def test_finserv_chat_agent_class_exists():
    source = _read_agent_source("agent/chat_agent.py")
    assert "class FinServChatAgent" in source, "FinServChatAgent class not found in chat_agent.py"


def test_finserv_chat_agent_has_chat_method():
    source = _read_agent_source("agent/chat_agent.py")
    assert "def chat(" in source, "chat() method not found in FinServChatAgent"


def test_finserv_chat_agent_has_load_history():
    """app.py calls agent.load_history() — must exist."""
    source = _read_agent_source("agent/chat_agent.py")
    assert "def load_history(" in source, "load_history() method not found in FinServChatAgent"


def test_finserv_chat_agent_has_clear_history():
    source = _read_agent_source("agent/chat_agent.py")
    assert "def clear_history(" in source, "clear_history() method not found"


def test_finserv_chat_agent_imports_both_subagents():
    source = _read_agent_source("agent/chat_agent.py")
    assert "AWSArchitectAgent" in source, "AWSArchitectAgent not imported in chat_agent.py"
    assert "GenAIMLAgent" in source, "GenAIMLAgent not imported in chat_agent.py"


def test_finserv_chat_agent_has_routing():
    """Router should classify messages as full analysis or quick answer."""
    source = _read_agent_source("agent/chat_agent.py")
    assert "FULL_ANALYSIS" in source or "_classify_message" in source, \
        "Message routing/classification not found in chat_agent.py"


# ─────────────────────────────────────────────────────────────────────────────
# 6. App.py interface contract
# ─────────────────────────────────────────────────────────────────────────────

def test_app_imports_finserv_chat_agent():
    source = _read_agent_source("app.py")
    assert "FinServChatAgent" in source, "app.py does not import FinServChatAgent"


def test_app_has_financial_services_branding():
    source = _read_agent_source("app.py")
    assert "Financial Services" in source, "Financial Services branding missing from app.py"
    assert "🏦" in source, "Bank emoji missing from app.py"


def test_app_has_entity_type_selector():
    """New customer form should have financial services entity types."""
    source = _read_agent_source("app.py")
    assert "Regional Bank" in source, "Financial services entity types missing from app.py"
    assert "FS_ENTITY_TYPES" in source, "FS_ENTITY_TYPES constant missing from app.py"


def test_app_save_exchange_simplified_signature():
    """_save_exchange in new app has simplified signature (no new_history_entries)."""
    source = _read_agent_source("app.py")
    # The new signature is _save_exchange(conv_id, user_prompt, assistant_response)
    # old had new_history_entries as 3rd param
    assert "def _save_exchange(" in source, "_save_exchange function missing"


def test_app_has_two_agent_status_messages():
    """Status callback should handle Phase 1 and Phase 2 messages."""
    source = _read_agent_source("app.py")
    assert "Phase 1" in source, "Phase 1 status message missing from app.py"
    assert "Phase 2" in source, "Phase 2 status message missing from app.py"


def test_app_uses_load_history_not_direct_history_assignment():
    """New app uses agent.load_history() instead of directly setting agent.history."""
    source = _read_agent_source("app.py")
    assert "load_history" in source, "load_history() not called in app.py"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Discovery agent financial services enhancements
# ─────────────────────────────────────────────────────────────────────────────

def test_discovery_agent_has_regulatory_context():
    source = _read_agent_source("agent/discovery_agent.py")
    assert "GLBA" in source, "GLBA missing from discovery agent"
    assert "PCI DSS" in source, "PCI DSS missing from discovery agent"
    assert "FFIEC" in source, "FFIEC missing from discovery agent"
    assert "SOX" in source, "SOX missing from discovery agent"


def test_discovery_agent_has_entity_type_detection():
    source = _read_agent_source("agent/discovery_agent.py")
    assert "Entity Type" in source or "entity type" in source.lower(), \
        "Entity type detection missing from discovery agent"
    assert "Regulatory Profile" in source, "Regulatory profile missing from discovery agent"


def test_discovery_agent_has_20_discovery_questions():
    """Brief should produce 20 discovery questions (up from 15 in original)."""
    source = _read_agent_source("agent/discovery_agent.py")
    assert "20 total" in source, "Discovery agent should produce 20 questions (4 personas × 5)"


def test_discovery_agent_has_compliance_risk_table():
    source = _read_agent_source("agent/discovery_agent.py")
    assert "Regulatory Risk" in source or "regulatory risk" in source.lower(), \
        "Regulatory risk assessment table missing from discovery agent"


def test_discovery_agent_has_cro_persona():
    """Financial services brief must include CRO/Chief Risk Officer persona."""
    source = _read_agent_source("agent/discovery_agent.py")
    assert "CRO" in source or "Chief Risk" in source, \
        "CRO/Chief Risk Officer persona missing from discovery agent"


# ─────────────────────────────────────────────────────────────────────────────
# 8. File structure integrity
# ─────────────────────────────────────────────────────────────────────────────

def test_new_agent_files_exist():
    """Both new agent files must exist."""
    assert (ROOT / "agent" / "aws_architect_agent.py").exists(), \
        "agent/aws_architect_agent.py does not exist"
    assert (ROOT / "agent" / "genai_ml_agent.py").exists(), \
        "agent/genai_ml_agent.py does not exist"


def test_all_agent_init_preserved():
    assert (ROOT / "agent" / "__init__.py").exists(), \
        "agent/__init__.py missing"


def test_vectorstore_preserved():
    assert (ROOT / "vectorstore" / "pg_client.py").exists(), \
        "vectorstore/pg_client.py missing"


def test_ingestion_pipeline_preserved():
    assert (ROOT / "ingestion" / "ingest_pipeline.py").exists(), \
        "ingestion/ingest_pipeline.py missing"


def test_requirements_txt_exists():
    assert (ROOT / "requirements.txt").exists(), "requirements.txt missing"

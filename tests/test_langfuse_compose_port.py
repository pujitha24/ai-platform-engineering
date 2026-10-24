import re
from pathlib import Path

import yaml


COMPOSE = Path(__file__).resolve().parents[1] / "docker-compose.yaml"


def _host_port(mapping: str) -> str:
    """Return the host-side part of a Compose `host:container` port mapping."""
    return mapping.rsplit(":", 1)[0]


def test_langfuse_web_does_not_share_host_port_with_caipe_ui() -> None:
    services = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"]

    ui_hosts = {_host_port(p) for p in services["caipe-ui"]["ports"]}
    langfuse_hosts = {_host_port(p) for p in services["langfuse-web"]["ports"]}

    assert not ui_hosts & langfuse_hosts


def test_langfuse_nextauth_url_follows_published_port() -> None:
    langfuse = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"]["langfuse-web"]
    env = dict(e.split("=", 1) for e in langfuse["environment"] if isinstance(e, str))

    port_var = re.search(r"\$\{(\w+):-(\d+)\}", langfuse["ports"][0])
    assert port_var is not None
    assert env["NEXTAUTH_URL"] == f"http://localhost:${{{port_var[1]}:-{port_var[2]}}}"

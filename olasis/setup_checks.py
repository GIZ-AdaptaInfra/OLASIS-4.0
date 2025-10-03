"""Utilities to diagnose Google Gemini configuration issues.

This module provides a small CLI that verifies whether the mandatory
runtime requirements for the Gemini-powered chatbot are satisfied.  It is
intended for local developers who frequently run into the
"chatbot indisponível" message when the dependency stack is incomplete.

Usage::

    python -m olasis.setup_checks

The command exits with status code 0 when every check passes, otherwise it
prints actionable guidance and returns a non-zero exit code.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from .dependencies import _format_pip_command  # type: ignore[attr-defined]


@dataclass
class CheckResult:
    """Result of a single diagnostic step."""

    name: str
    ok: bool
    message: str

    def format_line(self) -> str:
        status = "OK" if self.ok else "FAIL"
        return f"[{status}] {self.name}: {self.message}"


def _check_google_genai() -> CheckResult:
    """Verify that the ``google-genai`` package is available."""

    spec = importlib.util.find_spec("google.genai")
    if spec is None:
        hint = _format_pip_command()
        return CheckResult(
            name="google-genai",
            ok=False,
            message=(
                "Pacote ausente. Instale as dependências com:\n    "
                f"{hint}"
            ),
        )

    module = importlib.import_module("google.genai")
    has_client = hasattr(module, "Client")
    if not has_client:
        return CheckResult(
            name="google-genai",
            ok=False,
            message=(
                "O pacote está instalado, mas não expõe google.genai.Client. "
                "Atualize para a versão mais recente executando:\n    "
                f"{_format_pip_command()}"
            ),
        )

    return CheckResult(
        name="google-genai",
        ok=True,
        message="Biblioteca encontrada (google.genai.Client disponível)",
    )


def _check_api_key() -> CheckResult:
    """Ensure a Gemini API key is configured with a non-placeholder value."""

    placeholders = {
        "",
        "sua_chave_api_aqui",
        "sua_chave_google_gemini_aqui",
        "your_api_key",
        "coloque_sua_chave",
    }

    env_candidates: Sequence[Tuple[str, Optional[str]]] = (
        ("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY")),
        ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY")),
    )

    def _normalise(raw: Optional[str]) -> Optional[str]:
        if raw is None:
            return None
        stripped = raw.strip()
        if stripped.lower() in placeholders:
            return ""
        return stripped

    normalised_candidates: List[Tuple[str, Optional[str]]] = [
        (name, _normalise(value)) for name, value in env_candidates
    ]

    placeholder_sources = [
        name for name, value in normalised_candidates if value == ""
    ]

    for name, value in normalised_candidates:
        if value:
            if name == "GOOGLE_API_KEY":
                return CheckResult(
                    name="GOOGLE_API_KEY",
                    ok=True,
                    message="Chave configurada (valor não exibido por segurança)",
                )

            return CheckResult(
                name="GOOGLE_API_KEY",
                ok=True,
                message=(
                    "Chave configurada via GEMINI_API_KEY (valor não exibido por "
                    "segurança)."
                ),
            )

    if placeholder_sources:
        joined = ", ".join(placeholder_sources)
        return CheckResult(
            name="GOOGLE_API_KEY",
            ok=False,
            message=(
                "Valor em {vars} ainda é um placeholder. Substitua por uma chave real "
                "do Google Gemini."
            ).format(vars=joined),
        )

    export_hint = (
        "export GOOGLE_API_KEY=\"sua_chave_aqui\"  # ou defina GEMINI_API_KEY"
    )
    return CheckResult(
        name="GOOGLE_API_KEY",
        ok=False,
        message=(
            "Nenhuma chave configurada. Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) com "
            "sua credencial real, por exemplo:\n    {hint}"
        ).format(hint=export_hint),
    )


def _check_env_example_for_secrets() -> CheckResult:
    """Alert when a tracked .env.example appears to contain a real key."""

    path = Path(".env.example")
    if not path.exists():
        return CheckResult(
            name=".env.example",
            ok=True,
            message="Arquivo .env.example não encontrado (nenhuma verificação necessária)",
        )

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return CheckResult(
            name=".env.example",
            ok=False,
            message=f"Não foi possível ler .env.example: {exc}",
        )

    match = re.search(r"^GOOGLE_API_KEY=(.+)$", content, flags=re.MULTILINE)
    if not match:
        return CheckResult(
            name=".env.example",
            ok=True,
            message="Nenhuma linha GOOGLE_API_KEY= encontrada em .env.example",
        )

    value = match.group(1).strip().strip('"')
    placeholders = {
        "",
        "sua_chave_google_gemini_aqui",
        "sua_chave_api_aqui",
        "your_api_key",
        "coloque_sua_chave",
    }

    if value in placeholders:
        return CheckResult(
            name=".env.example",
            ok=True,
            message="Placeholder padrão preservado em .env.example",
        )

    looks_like_google = bool(re.fullmatch(r"AIza[0-9A-Za-z_-]{33}", value))
    if looks_like_google:
        return CheckResult(
            name=".env.example",
            ok=False,
            message=(
                "Possível chave real encontrada em .env.example. Mova o valor para o arquivo "
                ".env (não versionado) executando:\n    cp .env.example .env\n    "
                "# depois edite .env e remova a chave de .env.example para evitar exposição."
            ),
        )

    return CheckResult(
        name=".env.example",
        ok=True,
        message="Valor personalizado detectado; confirme se não é uma chave real",
    )


def run_diagnostics() -> List[CheckResult]:
    """Execute all configuration checks and return their results."""

    return [
        _check_google_genai(),
        _check_api_key(),
        _check_env_example_for_secrets(),
    ]


def _print_report(results: Iterable[CheckResult]) -> None:
    """Print human-readable feedback for each diagnostic result."""

    for result in results:
        print(result.format_line())


def main(argv: List[str] | None = None) -> int:
    """Entry-point for ``python -m olasis.setup_checks``."""

    results = run_diagnostics()
    _print_report(results)

    success = all(result.ok for result in results)
    if not success:
        print(
            "\n⚠️  Pelo menos uma verificação falhou. Corrija os itens acima e "
            "execute o comando novamente."
        )
        return 1

    print("\n✅ Ambiente pronto para usar o OLABOT.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    raise SystemExit(main(sys.argv[1:]))
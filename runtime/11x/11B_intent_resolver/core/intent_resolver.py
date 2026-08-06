"""STARCORE 11B — Human-AI Interface: Intent Resolver"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import re


@dataclass
class Intent:
    name: str
    confidence: float
    entities: dict[str, str] = field(default_factory=dict)
    slots: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentPattern:
    intent_name: str
    patterns: list[str]
    required_entities: list[str] = field(default_factory=list)


class IntentResolver:
    def __init__(self) -> None:
        self._patterns: list[IntentPattern] = []

    def register(self, pattern: IntentPattern) -> None:
        self._patterns.append(pattern)

    def resolve(self, utterance: str) -> list[Intent]:
        utterance_lower = utterance.lower()
        results: list[Intent] = []
        for ip in self._patterns:
            for pat in ip.patterns:
                if re.search(pat, utterance_lower):
                    entities = self._extract_entities(utterance, ip.required_entities)
                    confidence = 0.9 if len(entities) == len(ip.required_entities) else 0.6
                    results.append(Intent(
                        name=ip.intent_name,
                        confidence=confidence,
                        entities=entities,
                    ))
                    break
        return sorted(results, key=lambda i: i.confidence, reverse=True)

    def _extract_entities(self, text: str, entity_types: list[str]) -> dict[str, str]:
        found: dict[str, str] = {}
        words = text.split()
        for i, word in enumerate(words):
            for etype in entity_types:
                if etype.lower() in word.lower() and etype not in found:
                    found[etype] = word
        return found

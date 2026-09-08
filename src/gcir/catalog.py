"""The approved Control Derivation Catalog K (manuscript Section IV-B).

    k_j = (event_type, observable_class, allowed_producers, triple_template,
           allowed_operators, value_schema, evaluation_basis, evidence_schema,
           permitted_responses)

The single hard rule this module exists to enforce:

    "A register row whose approved event_type does not resolve to a catalog entry
     is not interpreted heuristically; it receives an unresolved or non-runtime
     disposition."  (Section IV-B)

    "if template == bottom: halt(UNRESOLVED_TEMPLATE, acs.acs_id)
     # heuristic matching prohibited"  (Appendix B)

Resolution is therefore an *exact* two-key lookup on ``(event_type, template_id)``.
There is deliberately no fuzzy match, no similarity score, no nearest-neighbour
fallback and no default template.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import CatalogResolutionError, ValidationError


class ControlDerivationCatalog:
    """An approved, versioned catalog.  Immutable once constructed."""

    def __init__(self, document):
        self._doc = document
        self._entries = {}
        for entry in document["entries"]:
            key = (entry["event_type"], entry["template_id"])
            if key in self._entries:
                raise ValidationError(
                    "duplicate catalog template %s/%s" % key,
                    code="DUPLICATE_CATALOG_ENTRY",
                    detail={"event_type": key[0], "template_id": key[1]},
                )
            self._entries[key] = entry

    # -- identity -----------------------------------------------------------

    @property
    def catalog_id(self):
        return self._doc["catalog_id"]

    @property
    def version(self):
        return self._doc["version"]

    @property
    def version_binding_ref(self):
        return self._doc["version_binding_ref"]

    @property
    def document(self):
        return self._doc

    @property
    def entries(self):
        return [self._entries[k] for k in sorted(self._entries)]

    def event_types(self):
        return sorted({event for event, _ in self._entries})

    def canonical_document(self):
        """The catalog as it enters the bundle hash.

        Section VI-C requires "deterministic array ordering where order is not
        semantically meaningful".  A catalog's entry sequence carries no meaning:
        entries are addressed by the (event_type, template_id) pair, never by
        position.  Hashing the document as authored would therefore leak the
        author's ordering into the bundle hash and break determinism under an
        equivalent input permutation -- which is exactly what the determinism
        experiment detected before this projection existed.

        The signature envelope is stripped for the same reason it lives outside
        the payload: it carries signing time and key identity.
        """
        document = {
            key: value
            for key, value in self._doc.items()
            if key not in ("signature", "entries")
        }
        document["entries"] = [self._entries[key] for key in sorted(self._entries)]
        return document

    # -- resolution ---------------------------------------------------------

    def exact_lookup(self, event_type, template_id):
        """Resolve exactly one approved template, or raise.

        This is the only lookup path in the codebase.  It performs no matching of
        any kind beyond dictionary equality.
        """
        entry = self._entries.get((event_type, template_id))
        if entry is None:
            raise CatalogResolutionError(
                "no approved catalog template for event_type=%r template_id=%r "
                "(heuristic matching is prohibited by Section IV-B)"
                % (event_type, template_id),
                detail={"event_type": event_type, "template_id": template_id},
            )
        return entry

    def has(self, event_type, template_id):
        return (event_type, template_id) in self._entries

    # -- template conformance ----------------------------------------------

    def check_acs_against_template(self, acs, template):
        """Validate an ACS against the catalog entry it selected.

        Implements compiler steps 4 and 5 of Section VI-A: action parameters
        against ``parameter_schema``, evidence type and producer against the
        selected catalog entry.
        """
        problems = []

        if acs["evaluation_basis"] != template["evaluation_basis"]:
            problems.append(
                "evaluation_basis %r is not the approved basis %r for this template"
                % (acs["evaluation_basis"], template["evaluation_basis"])
            )

        allowed_producers = template["allowed_producers"]
        if acs["observable_producer"] not in allowed_producers:
            problems.append(
                "observable_producer %r is not in the template's allowed_producers %r"
                % (acs["observable_producer"], allowed_producers)
            )

        if acs["operator"] not in template["allowed_operators"]:
            problems.append(
                "operator %r is not in the template's allowed_operators %r"
                % (acs["operator"], template["allowed_operators"])
            )

        if acs.get("observable_class") and acs["observable_class"] != template["observable_class"]:
            problems.append(
                "observable_class %r does not match template %r"
                % (acs["observable_class"], template["observable_class"])
            )

        # The triple template fixes which authority-matrix roles this event type
        # may bind.  A template for a publication event may not be reused to gate
        # a tool call.
        triple = template["triple_template"]
        for role in ("subject", "action", "resource", "destination"):
            allowed = triple.get(role)
            if allowed is None:
                continue
            if acs[role] not in allowed:
                problems.append(
                    "%s %r is not permitted by the template's triple_template %r"
                    % (role, acs[role], allowed)
                )

        evidence_schema = template["evidence_schema"]
        acs_evidence = acs.get("evidence_schema_ref")
        if acs_evidence != evidence_schema["schema_id"]:
            problems.append(
                "evidence_schema_ref %r does not resolve to the template's evidence "
                "schema %r" % (acs_evidence, evidence_schema["schema_id"])
            )

        response = acs.get("on_fail")
        if response not in template["permitted_responses"]:
            problems.append(
                "on_fail %r is not in the template's permitted_responses %r"
                % (response, template["permitted_responses"])
            )

        value_schema = template["value_schema"]
        expected = acs.get("expected_value")
        if not _value_matches_schema(expected, value_schema):
            problems.append(
                "expected_value %r does not satisfy the template value_schema %r"
                % (expected, value_schema)
            )

        if problems:
            raise ValidationError(
                "ACS %s does not conform to catalog template %s/%s: %s"
                % (
                    acs["acs_id"],
                    template["event_type"],
                    template["template_id"],
                    "; ".join(problems),
                ),
                code="TEMPLATE_CONFORMANCE_FAILURE",
                detail={"acs_id": acs["acs_id"], "problems": problems},
            )
        return True


def _value_matches_schema(value, schema):
    """A deliberately small structural type check -- no coercion, no inference."""
    kind = schema["type"]
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "string":
        if not isinstance(value, str):
            return False
        if "enum" in schema:
            return value in schema["enum"]
        return True
    if kind == "array":
        return isinstance(value, list)
    if kind == "null":
        return value is None
    return False


def load_catalog(document):
    return ControlDerivationCatalog(document)

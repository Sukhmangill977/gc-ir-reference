"""Load a committed case tree into ``CompilerInputs``.

This is the single entry point every experiment and test uses, so that "what the
compiler was given" is one auditable code path rather than several.
"""

from __future__ import annotations

import copy
import json
import os

from .catalog import ControlDerivationCatalog
from .compiler import CompilerInputs
from .coverage import CStarProfile
from .models import ApprovedControlSpecification, Assessment, Disposition, JudgmentRecord
from .signatures import KeyRing
from .validation import validate_document

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASES_DIR = os.path.join(REPO_ROOT, "cases")
KEYS_DIR = os.path.join(REPO_ROOT, "keys")

#: Which schema validates which committed file.
SCHEMA_MAP = (
    ("inputs/assessment.json", "assessment.schema.json"),
    ("inputs/control_derivation_catalog.json", "control_derivation_catalog.schema.json"),
    ("inputs/cstar_profile.json", "cstar_profile.schema.json"),
    ("inputs/invariant_register.json", "invariant_register.schema.json"),
    ("judgment/judgment_record.json", "judgment_record.schema.json"),
    ("dispositions/dispositions.json", "dispositions.schema.json"),
    ("acs/approved_control_specifications.json", "acs.schema.json"),
)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class CaseBundleInputs:
    """A loaded case: raw documents plus the assembled ``CompilerInputs``."""

    def __init__(self, case_id, root, documents, keyring):
        self.case_id = case_id
        self.root = root
        self.documents = documents
        self.keyring = keyring

    @property
    def parameters(self):
        return self.documents["compile_parameters"]

    def compiler_inputs(self, overrides=None):
        return build_compiler_inputs(self.documents, self.keyring, overrides or {})


def load_case(case_id, cases_dir=None, keys_dir=None, validate=True):
    root = os.path.join(cases_dir or CASES_DIR, case_id)
    documents = {}

    for relative, schema_name in SCHEMA_MAP:
        document = read_json(os.path.join(root, relative))
        if validate:
            validate_document(document, schema_name, label="%s/%s" % (case_id, relative))
        documents[os.path.basename(relative)[:-5]] = document

    documents["threshold_contracts"] = read_json(
        os.path.join(root, "inputs", "threshold_contracts.json")
    )
    documents["policy_metadata"] = read_json(
        os.path.join(root, "inputs", "policy_metadata.json")
    )
    documents["compile_parameters"] = read_json(
        os.path.join(root, "inputs", "compile_parameters.json")
    )

    if validate:
        for contract in documents["threshold_contracts"]["contracts"].values():
            validate_document(
                contract, "threshold_contract.schema.json",
                label="%s threshold contract %s" % (case_id, contract["contract_id"]),
            )

    keyring = KeyRing.load(keys_dir or KEYS_DIR)
    return CaseBundleInputs(case_id, root, documents, keyring)


def build_compiler_inputs(documents, keyring, overrides=None):
    """Assemble ``CompilerInputs`` from loaded documents.

    ``overrides`` lets the adversarial suite substitute a single mutated document
    without touching the committed tree.
    """
    overrides = overrides or {}
    documents = dict(documents)
    documents.update(overrides)

    raw_assessment = documents["assessment"]
    assessment = Assessment(
        metadata=raw_assessment["metadata"],
        system_profile=raw_assessment["system_profile"],
        obligations=raw_assessment["obligations"],
        risk_register=raw_assessment["risk_register"],
        risk_analysis=raw_assessment["risk_analysis"],
    )

    catalog = ControlDerivationCatalog(documents["control_derivation_catalog"])
    cstar = CStarProfile(documents["cstar_profile"])
    judgment_doc = documents["judgment_record"]
    judgment = JudgmentRecord(
        judgment_id=judgment_doc["judgment_id"],
        version=judgment_doc["version"],
        assessment_ref=judgment_doc["assessment_ref"],
        catalog_ref=judgment_doc["catalog_ref"],
        selections=judgment_doc["selections"],
        approvals=judgment_doc["approvals"],
        signature=judgment_doc.get("signature"),
    )
    dispositions = [
        Disposition.from_mapping(record)
        for record in documents["dispositions"]["records"]
    ]
    acs_records = [
        ApprovedControlSpecification(record)
        for record in documents["approved_control_specifications"]["records"]
    ]
    invariants = documents["invariant_register"]["invariants"]
    parameters = documents["compile_parameters"]

    signatures = {
        "assessment": (raw_assessment, "assessment"),
        "catalog": (documents["control_derivation_catalog"], "catalog"),
        "cstar_profile": (documents["cstar_profile"], "cstar_profile"),
        "judgment_record": (judgment_doc, "judgment_record"),
        "dispositions": (documents["dispositions"], "dispositions"),
        "acs": (documents["approved_control_specifications"], "acs"),
        "invariants": (documents["invariant_register"], "invariants"),
    }

    return CompilerInputs(
        assessment=assessment,
        catalog=catalog,
        judgment=judgment,
        dispositions=dispositions,
        acs_records=acs_records,
        invariants=invariants,
        cstar_profile=cstar,
        threshold_contracts=documents["threshold_contracts"]["contracts"],
        compile_time=parameters["compile_time"],
        signatures=signatures,
        keyring=keyring,
        signing_authorities=parameters["signing_authorities"],
        policy_metadata=documents["policy_metadata"],
        bundle_effective_from=parameters["bundle_effective_from"],
    )


def deep_copy_documents(documents):
    return copy.deepcopy(documents)

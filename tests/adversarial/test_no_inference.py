"""Static assertion that no probabilistic or similarity-based selection exists
anywhere in the shipped compiler path.

    "No best-match, similarity, or probabilistic rule selection is permitted
     inside Phi."  (Sections IV-A, VI-A, VI-B)

This is a source-level check rather than a behavioural one, because the claim is
about what the compiler *cannot* do, not about what it happened not to do on two
cases.
"""

import ast
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO_ROOT, "src", "gcir")

#: Modules that constitute Phi and everything it calls.
COMPILER_PATH_MODULES = [
    "compiler.py", "catalog.py", "refinement.py", "authority.py", "coverage.py",
    "canonicalization.py", "validation.py", "models.py", "precedence.py",
    "lifecycle.py", "temporal.py", "signatures.py", "metrics.py", "caseio.py",
    "traceability.py",
]

#: Identifiers whose presence would indicate inference, similarity or randomness.
FORBIDDEN_IDENTIFIERS = {
    "random", "randint", "randrange", "shuffle", "sample", "choice", "choices",
    "uniform", "gauss", "seed",
    "embed", "embedding", "embeddings", "encode_text", "vectorize",
    "cosine", "cosine_similarity", "similarity", "levenshtein", "jaccard",
    "fuzzy", "fuzz", "ratio_matcher", "get_close_matches", "SequenceMatcher",
    "best_match", "nearest", "knn", "argmax_score", "softmax", "predict",
    "predict_proba", "classify_text", "llm", "openai", "anthropic", "completion",
    "chat_completion", "prompt",
}

FORBIDDEN_IMPORTS = {
    "random", "secrets", "numpy.random", "difflib", "sklearn", "scipy",
    "torch", "tensorflow", "transformers", "sentence_transformers",
    "openai", "anthropic", "langchain", "llama_index", "faiss", "annoy",
    "rapidfuzz", "fuzzywuzzy", "Levenshtein", "gensim", "spacy", "nltk",
}

#: Clock access is forbidden inside the compiler path: the compile time is a
#: declared input, and no timestamp may enter the hashed payload.
FORBIDDEN_CLOCK_CALLS = {"now", "utcnow", "today", "time", "monotonic", "perf_counter"}
CLOCK_MODULES = {"time", "datetime"}


def _modules():
    for name in COMPILER_PATH_MODULES:
        path = os.path.join(SRC, name)
        with open(path, encoding="utf-8") as handle:
            yield name, path, ast.parse(handle.read(), filename=path)


@pytest.mark.parametrize("name", COMPILER_PATH_MODULES)
def test_no_forbidden_imports(name):
    path = os.path.join(SRC, name)
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if alias.name in FORBIDDEN_IMPORTS or root in FORBIDDEN_IMPORTS:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if node.module in FORBIDDEN_IMPORTS or root in FORBIDDEN_IMPORTS:
                found.append(node.module)
    assert not found, "%s imports %s" % (name, found)


@pytest.mark.parametrize("name", COMPILER_PATH_MODULES)
def test_no_probabilistic_or_similarity_selection(name):
    path = os.path.join(SRC, name)
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            called = None
            if isinstance(target, ast.Name):
                called = target.id
            elif isinstance(target, ast.Attribute):
                called = target.attr
            if called and called.lower() in {i.lower() for i in FORBIDDEN_IDENTIFIERS}:
                found.append("%s (line %d)" % (called, node.lineno))
        elif isinstance(node, ast.FunctionDef):
            if node.name.lower() in {i.lower() for i in FORBIDDEN_IDENTIFIERS}:
                found.append("def %s (line %d)" % (node.name, node.lineno))
    assert not found, "%s contains probabilistic/similarity selection: %s" % (name, found)


@pytest.mark.parametrize("name", COMPILER_PATH_MODULES)
def test_no_clock_access_in_the_compiler_path(name):
    """Section VI-C: 'no timestamp or random nonce inside the hashed payload'.

    The strongest form of that guarantee is that the compiler path never reads a
    clock at all, so a timestamp cannot reach the payload even by accident.
    """
    if name in ("caseio.py",):  # loads files; still must not read a clock
        pass
    path = os.path.join(SRC, name)
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attribute = node.func.attr
            if attribute not in FORBIDDEN_CLOCK_CALLS:
                continue
            value = node.func.value
            root = None
            while isinstance(value, ast.Attribute):
                value = value.value
            if isinstance(value, ast.Name):
                root = value.id
            if root in CLOCK_MODULES or root in {"_dt"}:
                found.append("%s.%s (line %d)" % (root, attribute, node.lineno))
    assert not found, "%s reads a clock: %s" % (name, found)


def test_catalog_resolution_is_a_dict_lookup_only():
    """The one place a template could be chosen heuristically is the catalog.

    ``exact_lookup`` must contain nothing but a dictionary ``get`` and a raise.
    The check is on the parsed function body, not on the file's text, so the
    module docstring explaining that there is no similarity matching cannot
    itself trip the assertion.
    """
    path = os.path.join(SRC, "catalog.py")
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)

    lookup = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "exact_lookup"
    )

    call_names = set()
    for node in ast.walk(lookup):
        if isinstance(node, ast.Call):
            func = node.func
            call_names.add(
                func.attr if isinstance(func, ast.Attribute)
                else getattr(func, "id", "<computed>")
            )
    assert call_names <= {"get", "CatalogResolutionError"}, (
        "exact_lookup calls %s; it must be a dictionary lookup and a raise, nothing more"
        % sorted(call_names)
    )

    # No comparison operator other than the identity test against None: any
    # ordering or membership test would be the beginning of a match heuristic.
    comparisons = [
        type(op).__name__
        for node in ast.walk(lookup) if isinstance(node, ast.Compare)
        for op in node.ops
    ]
    assert set(comparisons) <= {"Is", "IsNot"}, comparisons

    # No loop: resolution cannot scan candidates.
    loops = [n for n in ast.walk(lookup) if isinstance(n, (ast.For, ast.While))]
    assert not loops, "exact_lookup must not iterate over candidate templates"

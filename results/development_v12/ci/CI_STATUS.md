# Cross-platform determinism -- CI status

Measured by `.github/workflows/determinism.yml`. Each matrix leg compiles
both cases and runs the determinism experiment; this table is generated
from the uploaded result files.

| CI leg | platform | python | TD | runs | Case A hash | Case B hash |
|---|---|---|---|---|---|---|
| determinism-macos-latest-py3.11 | macOS-26.6.2-arm64-arm-64bit | 3.11.9 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| determinism-macos-latest-py3.12 | macOS-26.6.2-arm64-arm-64bit | 3.12.10 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| determinism-ubuntu-latest-py3.11 | Linux-6.17.0-1022-azure-x86_64-with-glibc2.39 | 3.11.16 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| determinism-ubuntu-latest-py3.12 | Linux-6.17.0-1022-azure-x86_64-with-glibc2.39 | 3.12.14 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| determinism-windows-latest-py3.11 | Windows-10-10.0.26100-SP0 | 3.11.9 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| determinism-windows-latest-py3.12 | Windows-2025Server-10.0.26100-SP0 | 3.12.10 | 1.0 | 62 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |

Committed reference hashes:

| case | canonical payload SHA-256 |
|---|---|
| case_a | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| case_b | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |

**Supportable wording:** deterministic across the tested supported
environments. **Not** platform independence -- three runner images are not
the set of all environments (manuscript Section XII, determinism scope).

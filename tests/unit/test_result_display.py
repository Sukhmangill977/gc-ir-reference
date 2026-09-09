"""Presentation-only tests: all evidence mutations use temporary copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tools import show_results as viewer
from tools import update_readme_results as readme

ROOT = Path(viewer.REPO_ROOT)


@pytest.fixture
def copied_repo(tmp_path, monkeypatch):
    for directory in ('results/final_v2', 'artifact_review', 'cases'):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    for filename in ('MANIFEST.json', 'README.md', 'CITATION.cff'):
        shutil.copy2(ROOT / filename, tmp_path / filename)
    monkeypatch.setattr(viewer, 'REPO_ROOT', str(tmp_path))
    return tmp_path


def test_known_frozen_values():
    data = viewer.load_results()
    assert data['metrics']['case_a']['RCY']['value'] == 0.8125
    assert data['metrics']['case_a']['NDR']['value'] == 0.1875
    assert data['metrics']['case_b']['GD_min']['value'] == 0
    assert data['determinism']['total'] == 62
    assert data['monte_carlo']['case_a']['max_FP_heat'] == 0.321268
    assert data['verification']['tests_total'] == 280
    assert data['verification']['generated_examples'] == 1427
    assert data['_consistency']['ok']


def test_json_cli():
    run = subprocess.run([sys.executable, str(ROOT / 'tools/show_results.py'), '--json'],
                         capture_output=True, text=True, check=True, cwd=ROOT.parent)
    data = json.loads(run.stdout)
    assert data['consistent'] is True
    assert data['determinism']['passed'] == 62


def test_text_sections(capsys):
    assert viewer.main([]) == 0
    output = capsys.readouterr().out
    for title in ('PROVENANCE', 'CASE ARTIFACTS', 'PRIMARY METRICS', 'DETERMINISM',
                  'CROSS-PLATFORM', 'MONTE CARLO', 'TEST / VALIDATION SUMMARY',
                  'CLAIM BOUNDARY', 'REPORTABLE ARTIFACT VERIFIED'):
        assert title in output
    assert '\x1b' not in output


@pytest.mark.parametrize('relative', ['metrics.json', 'monte_carlo_summary.json',
                                      'property_tests.json', 'freeze_verification.json'])
def test_corrupt_source_fails(copied_repo, relative, capsys):
    path = copied_repo / 'results/final_v2' / relative
    blob = json.loads(path.read_text(encoding="utf-8"))
    blob['corrupt_value'] = True
    if relative == 'metrics.json':
        blob['result']['per_case']['case_a']['RCY']['value'] = 0.5
    path.write_text(json.dumps(blob))
    assert viewer.main([]) != 0
    assert readme.main(['--check']) != 0
    output = capsys.readouterr()
    assert 'checksum mismatch' in output.err
    assert 'REPORTABLE ARTIFACT VERIFIED' not in output.out
    assert 'Traceback' not in output.err


def test_missing_evidence_fails(copied_repo, capsys):
    (copied_repo / 'results/final_v2/metrics.json').unlink()
    assert viewer.main([]) == 2
    assert 'required result file is missing' in capsys.readouterr().err


def test_missing_ci_leg_fails(copied_repo):
    next((copied_repo / 'results/final_v2/cross_environment/ci').glob('*/determinism_summary.json')).unlink()
    with pytest.raises(viewer.MissingEvidence, match='missing'):
        viewer.load_results()


def test_stale_readme_is_nonmutating(copied_repo, capsys):
    path = copied_repo / 'README.md'
    path.write_text(path.read_text(encoding="utf-8").replace('| DC | 1.000', '| DC | 0.500'), encoding="utf-8")
    before = path.read_bytes()
    assert readme.main(['--check']) == 1
    assert path.read_bytes() == before
    assert 'stale' in capsys.readouterr().err


def test_updater_preserves_every_byte_outside_markers(copied_repo):
    path = copied_repo / 'README.md'
    original = 'prefix\r\nUnrelated π\n' + readme.BEGIN + '\nstale\n' + readme.END + '\r\nSuffix\n'
    path.write_bytes(original.encode())
    assert readme.main([]) == 0
    updated = path.read_bytes().decode()
    assert updated.startswith('prefix\r\nUnrelated π\n' + readme.BEGIN)
    assert updated.endswith(readme.END + '\r\nSuffix\n')
    assert readme.main(['--check']) == 0
    before = path.read_bytes()
    assert readme.main([]) == 0
    assert path.read_bytes() == before


@pytest.mark.parametrize('text', ['', readme.END + readme.BEGIN, readme.BEGIN * 2 + readme.END])
def test_invalid_markers_rejected(text):
    with pytest.raises(ValueError):
        readme.replace_block(text, 'new')


def test_provenance_document_matches_loader():
    assert (ROOT / 'artifact_review/RESULT_DISPLAY_PROVENANCE.md').read_text(encoding="utf-8") == readme.render_provenance(viewer.load_results())

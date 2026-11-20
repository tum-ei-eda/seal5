"""Quiet console logging must not discard successful lit test results."""
from seal5.tools import llvm


def test_quiet_runner_requests_and_records_pass_lines(tmp_path, monkeypatch):
    source = tmp_path / 'example.ll'
    source.write_text('; fixture\n')
    seen = []

    def execute(*args, **kwargs):
        seen.append(args)
        assert '--verbose' in args
        return 'PASS: LLVM :: example.ll (1 of 1)\n'

    monkeypatch.setattr(llvm.utils, 'exec_getout', execute)
    passed, failed = llvm.test_llvm(tmp_path, tmp_path / 'build', [str(source)], verbose=False)
    assert len(seen) == 1
    assert passed == ['example.ll']
    assert failed == []


def test_lit_startup_failure_cannot_report_success(tmp_path, monkeypatch):
    import pytest
    source = tmp_path / 'example.ll'
    source.write_text('; fixture\n')
    monkeypatch.setattr(llvm.utils, 'exec_getout', lambda *args, **kwargs: "Traceback: missing standard library")
    with pytest.raises(RuntimeError, match='no PASS/FAIL results'):
        llvm.test_llvm(tmp_path, tmp_path / 'build', [str(source)])


def test_reduced_build_includes_required_lit_utilities(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(llvm.utils, 'make', lambda *args, **kwargs: seen.append(kwargs['target']))
    llvm.build_llvm(tmp_path, tmp_path / 'build', skip_configure=True, reduced=True)
    assert 'count' in seen[0] and 'not' in seen[0]


def test_reduced_install_excludes_build_only_utilities(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(llvm.utils, 'make', lambda *args, **kwargs: seen.append(kwargs['target']))
    llvm.build_llvm(tmp_path, tmp_path / 'build', target=None, skip_configure=True,
                    reduced=True, install=True, install_dir=tmp_path / 'install')
    assert 'install-count' not in seen[0] and 'install-not' not in seen[0]


def test_report_uses_latest_test_attempt():
    from seal5.backends.report.test_results.writer import latest_test_metrics
    old = {'passed': [], 'failing': ['old-failure']}
    new = {'passed': ['new-success'], 'failing': []}
    assert latest_test_metrics([{'test': old}, {'build': {}}, {'test': new}]) is new
    assert latest_test_metrics([{'build': {}}]) is None

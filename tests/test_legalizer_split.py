"""Keep each LLVM version's min/max legality rules when unsharing builders."""
import pytest
from seal5.tools.cdsl2llvm import split_minmax_legalizer_actions


@pytest.mark.parametrize('body', [
    '''  auto &MinMaxActions =
      getActionDefinitionsBuilder({G_UMAX, G_UMIN, G_SMAX, G_SMIN});
  if (ST.hasStdExtZbb())
    MinMaxActions.legalFor({sXLen}).minScalar(0, sXLen);
  MinMaxActions.lower();''',
    '''  getActionDefinitionsBuilder({G_UMAX, G_UMIN, G_SMAX, G_SMIN})
      .legalFor(ST.hasStdExtZbb(), {sXLen})
      .minScalar(ST.hasStdExtZbb(), 0, sXLen)
      .lower();''',
])
def test_split_preserves_rules_and_surrounding_code(body):
    source = '// before\n' + body + '\n// after\n'
    result = split_minmax_legalizer_actions(source)
    assert result.startswith('// before\n') and result.endswith('\n// after\n')
    assert 'for (unsigned Opcode : {G_UMAX, G_UMIN, G_SMAX, G_SMIN}) {' in result
    assert 'getActionDefinitionsBuilder(Opcode)' in result
    assert '.legalFor(' in result and '.minScalar(' in result
    assert result.count('.lower();') == 1
    for line in body.splitlines()[2:]:
        assert line.strip() in result


def test_unknown_source_fails_explicitly():
    with pytest.raises(ValueError, match='Cannot find the shared'):
        split_minmax_legalizer_actions('unrecognized source')

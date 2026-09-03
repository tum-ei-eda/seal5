#!/bin/bash

set -e

if [[ $# -ne 1 ]]
then
    echo "Invalid number of arguments!"
    exit 1
fi

LLVM_DIR=$1

if [[ ! -d "$LLVM_DIR" ]]
then
    echo "Not a directory: $LLVM_DIR"
    exit 1
fi

META_DIR=$LLVM_DIR/.seal5
REPORTS_DIR=$META_DIR/reports

mkdir -p $REPORTS_DIR

echo "REPORTS_DIR=$REPORTS_DIR"

# Properties
python3 -m seal5.backends.report.properties.writer $META_DIR/models/*.seal5model --output $REPORTS_DIR/properties.csv
python3 -m seal5.backends.report.properties.writer $META_DIR/models/*.seal5model --output $REPORTS_DIR/properties.md
# echo "### Properties" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/properties.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY

# Status
python3 -m seal5.backends.report.status.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --output $REPORTS_DIR/status.csv
python3 -m seal5.backends.report.status.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --compact --output $REPORTS_DIR/status_compact.csv
python3 -m seal5.backends.report.status.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --output $REPORTS_DIR/status.md --markdown-icons
python3 -m seal5.backends.report.status.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --compact --output $REPORTS_DIR/status_compact.md --markdown-icons
# echo "### Passes" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/status_compact.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY

# Test Results
python3 -m seal5.backends.report.test_results.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --output $REPORTS_DIR/test_results.csv --coverage $REPORTS_DIR/test_coverage.csv
python3 -m seal5.backends.report.test_results.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --compact --output $REPORTS_DIR/test_results_compact.csv --coverage $REPORTS_DIR/test_coverage_compact.csv
python3 -m seal5.backends.report.test_results.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --output $REPORTS_DIR/test_results.md --coverage $REPORTS_DIR/test_coverage.md --markdown-icons
python3 -m seal5.backends.report.test_results.writer $META_DIR/models/*.seal5model --yaml $META_DIR/settings.yml --compact --output $REPORTS_DIR/test_results_compact.md --coverage $REPORTS_DIR/test_coverage_compact.md --markdown-icons
# echo "### Test Coverage" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/test_coverage_compact.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# echo "### Test Results" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/test_results_compact.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY

# Diff
python3 -m seal5.backends.report.diff.writer --yaml $META_DIR/settings.yml --output $REPORTS_DIR/diff.csv
python3 -m seal5.backends.report.diff.writer --yaml $META_DIR/settings.yml --output $REPORTS_DIR/diff.md
# echo "### Diff" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/diff.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY

# Stage Times
python3 -m seal5.backends.report.times.writer --yaml $META_DIR/settings.yml --pass-times --output $REPORTS_DIR/stage_times.csv --sum-level 2
python3 -m seal5.backends.report.times.writer --yaml $META_DIR/settings.yml --pass-times --output $REPORTS_DIR/stage_times.md --sum-level 2
python3 -m seal5.backends.report.times.writer --yaml $META_DIR/settings.yml --pass-times --output $REPORTS_DIR/stage_times.mermaid --sum-level 2
# echo "### Stage/Pass Times" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/stage_times.md >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# echo "\`\`\`mermaid" >> $GITHUB_STEP_SUMMARY
# cat $REPORTS_DIR/stage_times.mermaid >> $GITHUB_STEP_SUMMARY
# echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
python3 seal5/examples/merge_test_artifacts.py $REPORTS_DIR/status_compact.csv $REPORTS_DIR/properties.csv  $REPORTS_DIR/test_results_compact.csv $REPORTS_DIR/test_coverage_compact.csv
# echo "### Summarized and Compact Pass/Test Results" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat  Grouped_stat_prop_result_test_wo_instr.html >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# echo "### Summarized and Compact Test Coverage Results" >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY
# cat  Grouped_stat_prop_result_cv_wo_instr.html >> $GITHUB_STEP_SUMMARY
# echo >> $GITHUB_STEP_SUMMARY

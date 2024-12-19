#!/usr/bin/env python

import argparse
import pathlib
import math
import pandas as pd
import numpy as np

pd.options.display.max_rows = 9999

def main():
    """Main function."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Merge SEAL5 Test Results")#,
               #formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("status_file",  type=str, help="Path to the status file")
    parser.add_argument("properties_file", type=str,  help="Path to the file of instruction properties")
    parser.add_argument("test_results",  type=str,  help="Path to the file containing seal5 test result file name")
    parser.add_argument("test_cv_file",  type=str,  help="Path to the file containing seal5 test coverage results" )
    args = parser.parse_args()

    if args.status_file:
        status_path = pathlib.Path(args.status_file)
        status_df = pd.read_csv(pathlib.Path(args.status_file))
    else:
       print('Path to status file must be specified')
   
    if args.test_results:
        test_result_df = pd.read_csv(pathlib.Path(args.test_results))
    else:
       print('Path to Test Results file must be specified')

    if args.properties_file:
        props_df = pd.read_csv(pathlib.Path(args.properties_file))
    else:
       print('Path to Instruction Properties file must be specified')

    if (args.test_cv_file):
        test_cv_df = pd.read_csv(pathlib.Path(args.test_cv_file))
    else:
       print('Path to Test Coverage file must be specified')    

    status_props_df = pd.merge(status_df, props_df)
    stat_prop_result_df = pd.merge(status_props_df, test_result_df, on=['model', 'set', 'xlen', 'instr'], how="left")

    stat_prop_result_df = stat_prop_result_df.sort_values("model")
    stat_prop_result_df.fillna(value = 0, 
          inplace = True)
     
    stat_prop_result_cv_df = pd.merge( stat_prop_result_df, test_cv_df, on=['model', 'set', 'xlen', 'instr'], how='left')

    def save_data_frames_as_html_to_file(dataframe, filename):
        with open(filename, 'w') as html_file:
            print(dataframe.to_html(buf=html_file, index=True))


    def calc_stage_percentage( ):
       perc_success = (((stat_prop_result_cv_df['n_success'] *100) / stat_prop_result_cv_df['n_total']).astype(int))
       perc_skipped = (((stat_prop_result_cv_df['n_skipped'] *100) / stat_prop_result_cv_df['n_total']).astype(int))
       perc_failed  = (((stat_prop_result_cv_df['n_failed'] *100) / stat_prop_result_cv_df['n_total']).astype(int))

       perc_result = '['+ round(perc_success,2).astype(str) +'%' + ' / '+ round(perc_skipped,2).astype(str) +'%'+ ' / '+ round(perc_failed,2).astype(str) +'%'+ ']'
       return perc_result;

    def calc_stage_percentage_sum( ):
       perc_success = (((stat_prop_result_cv_df['n_success'].sum() *100) / stat_prop_result_cv_df['n_total'].sum() ).astype(int))
       perc_skipped = (((stat_prop_result_cv_df['n_skipped'].sum() *100) / stat_prop_result_cv_df['n_total'].sum() ).astype(int))
       perc_failed  = (((stat_prop_result_cv_df['n_failed'].sum() *100) / stat_prop_result_cv_df['n_total'].sum() ).astype(int))

       perc_result = '['+ round(perc_success,2).astype(str)  +'%' + ' / '+ round(perc_skipped,2).astype(str) +'%'+ ' / '+ round(perc_failed,2).astype(str)  +'%'+ ']'
       return perc_result;

    def rounded_mean(x):
        return x.mean().round(1);
       
    stat_prop_result_cv_df.set_index(['model', 'enc_format', 'opcode'], inplace=True)
    
    stat_prop_result_cv_df2 = stat_prop_result_cv_df.groupby(level=[0,1,2])[['instr','n_success', 'n_failed',  'n_skipped',  'n_total', 'status' ]].agg({'instr':'unique', 'status': 'unique', 'n_success': rounded_mean, 'n_failed': 'mean',  'n_skipped':'mean',  'n_total' : 'mean'}) 
    
    stat_prop_result_cv_test = stat_prop_result_cv_df.groupby(level=[0,1,2])[['n_pass', 'n_fail',  'n_tests','state' ]].agg({'n_pass':rounded_mean, 'n_fail':rounded_mean,  'n_tests':rounded_mean, 'state':'unique'})

    stat_prop_result_coverage = stat_prop_result_cv_df.groupby(level=[0,1,2])[['n_exists', 'n_required' , 'n_optional', 'n_extra', 'n_required_exists', 'n_optional_exists', 'coverage' ]].agg({'n_exists':rounded_mean, 'n_required':rounded_mean , 'n_optional':rounded_mean, 'n_extra':rounded_mean, 'n_required_exists':rounded_mean, 'n_optional_exists':rounded_mean, 'coverage':'unique'}) 

   
    def calc_stage_percentage2( ):
       perc_success = (((stat_prop_result_cv_df2['n_success'] *100) / stat_prop_result_cv_df2['n_total'] ).astype(int)).astype(str)
       perc_skipped = (((stat_prop_result_cv_df2['n_skipped'] *100) / stat_prop_result_cv_df2['n_total'] ).astype(int)).astype(str)
       perc_failed  = (((stat_prop_result_cv_df2['n_failed'] *100) / stat_prop_result_cv_df2['n_total'] ).astype(int)).astype(str)

       perc_result = '['+ perc_success +'%' + ' / '+ perc_skipped +'%'+ ' / '+ perc_failed +'%'+ ']'
       return perc_result;

    def calc_stage_percentage2_sum( ):
       perc_success = (((stat_prop_result_cv_df2['n_success'].sum() *100) / stat_prop_result_cv_df2['n_total'].sum() ).astype(int)).astype(str)
       perc_skipped = (((stat_prop_result_cv_df2['n_skipped'].sum() *100) / stat_prop_result_cv_df2['n_total'].sum() ).astype(int)).astype(str)
       perc_failed  = (((stat_prop_result_cv_df2['n_failed'].sum() *100) / stat_prop_result_cv_df2['n_total'].sum() ).astype(int)).astype(str)

       perc_result = '['+ perc_success +'%' + ' / '+ perc_skipped +'%'+ ' / '+ perc_failed +'%'+ ']'
       return perc_result;



    def calc_test_percentage( ):
       perc_pass = (((stat_prop_result_cv_test['n_pass'] *100) / stat_prop_result_cv_test['n_tests']))
       perc_fail = (((stat_prop_result_cv_test['n_fail'] *100) / stat_prop_result_cv_test['n_tests']))

       perc_result = '['+ round(perc_pass,2).astype(str) +'%' + ' / '+ round(perc_fail,2).astype(str) +'%'+ ']'
       return perc_result;

    def calc_test_percentage_sum( ):
       perc_pass = (((stat_prop_result_cv_test['n_pass'].sum() *100) / stat_prop_result_cv_test['n_tests'].sum() ).astype(int))
       perc_fail = (((stat_prop_result_cv_test['n_fail'].sum() *100) / stat_prop_result_cv_test['n_tests'].sum() ).astype(int))

       perc_result = '['+ round(perc_pass,2).astype(str) +'%' + ' / '+ round(perc_fail,2).astype(str) +'%'+ ']'
       return perc_result;

    stat_result_summary =  stat_prop_result_cv_df2["n_success"].astype(str)+' / '+ stat_prop_result_cv_df2["n_skipped"].astype(str) +' / '+ stat_prop_result_cv_df2["n_failed"].astype(str)+ ' ' + calc_stage_percentage2()
    stat_prop_result_cv_df2.insert(loc=1, column='Status_Summary: (Passed/Skipped/Failed) %', value=stat_result_summary)

    stat_prop_test_summary = stat_prop_result_cv_test["n_pass"].astype(str)+' / '+ stat_prop_result_cv_test["n_fail"].astype(str)+ ' ' + calc_test_percentage()
    stat_prop_result_cv_df2.insert(loc=1, column=' Summary Test Results: (Passed/Failed) % ', value=stat_prop_test_summary)

    #'n_exists', 'n_required' , 'n_optional', 'n_extra', 'n_required_exists', 'n_optional_exists'

    final_status_results = stat_prop_result_cv_df2.drop('n_success', axis=1).drop('n_failed', axis=1).drop('n_skipped', axis=1).drop('n_total', axis=1)
    final_test_results = stat_prop_result_cv_test.drop('n_pass', axis=1).drop('n_fail', axis=1).drop('n_tests', axis=1)
    final_coverage_results = stat_prop_result_coverage.drop('n_exists', axis=1).drop('n_required', axis=1).drop('n_optional', axis=1)
   
    final_test_table = pd.merge(final_status_results, final_test_results , on=['model', 'enc_format', 'opcode'], how='inner')
    final_coverage_table = pd.merge(final_test_table, final_coverage_results , on=['model', 'enc_format', 'opcode'], how='inner')

    save_data_frames_as_html_to_file(final_test_table, "Grouped_stat_prop_result_test.html")
    save_data_frames_as_html_to_file(final_coverage_table, "Grouped_stat_prop_result_cv.html")
    save_data_frames_as_html_to_file(stat_prop_result_cv_df, "Grouped_stat_prop_result_all.html")


    final_test_table = final_coverage_table.drop('instr', axis=1)
    final_coverage_table = final_coverage_table.drop('instr', axis=1)
    save_data_frames_as_html_to_file(final_test_table, "Grouped_stat_prop_result_test_wo_instr.html")
    save_data_frames_as_html_to_file(final_coverage_table, "Grouped_stat_prop_result_cv_wo_instr.html")
    
    print(final_test_results)
    print(final_status_results)


    print(final_test_table)  
    print(final_coverage_table)

if __name__ == "__main__":
    main()



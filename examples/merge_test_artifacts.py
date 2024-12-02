#!/usr/bin/env python

import argparse
import pathlib

import pandas as pd

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

    if args.properties_file:
        props_df = pd.read_csv(pathlib.Path(args.properties_file))

    if (args.test_cv_file):
        test_cv_df = pd.read_csv(pathlib.Path(args.test_cv_file))

    status_props_df = pd.merge(status_df, props_df)
    stat_prop_result_df = pd.merge(status_props_df, test_result_df, on=['model', 'set', 'xlen', 'instr'], how="left")

    stat_prop_result_df = stat_prop_result_df.sort_values("model")
    stat_prop_result_df.fillna('N/A')

    stat_prop_result_cv_df = pd.merge( stat_prop_result_df, test_cv_df, on=['model', 'set', 'xlen', 'instr'], how='left')

    def save_data_frames_as_md(dataframe, filename):
        with open(filename, 'w') as md:
            print(dataframe.to_html(buf=md, index=True"))

    save_data_frames_as_md(stat_prop_result_df, "stat_prop_result_df.md")
    save_data_frames_as_md(stat_prop_result_cv_df, "stat_prop_result_cv_df.md")

    stat_prop_result_cv_df1 = stat_prop_result_cv_df;

    stat_prop_result_cv_df2 = stat_prop_result_cv_df;
    
    stat_prop_result_cv_df1.set_index(['model', 'set', 'enc_format', 'opcode', 'instr'], inplace=True)

    stat_prop_result_cv_df1 = stat_prop_result_cv_df1.groupby(level=[0,1,2,3,4])[['n_success',  'n_optional',  'n_extra',  'n_required_exists', 'n_optional_exists']].mean()
  
    save_data_frames_as_md(stat_prop_result_cv_df1, "Grouped_stat_prop_result_cv.md")
    save_data_frames_as_md(stat_prop_result_cv_df2, "Grouped_stat_prop_result_all.md")

if __name__ == "__main__":
    main()



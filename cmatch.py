#!/usr/bin/env python

import json
import logging
import os
from os import path
from pathlib import Path
import time
from reconstruction import reconstruct
import math
import streamlit as st

from futils import timeit
from tqdm import tqdm

from matching import Library, Sequence, match_library
from visualise import visualise_distribution, plot_error_types, visualise_parts, plot_3d_multiple_scores
from store_outputs_to_parquet import store_match_results

import plac


# Logging configuration
current_file = path.basename(__file__).split(".")[0]


@timeit
def match_libs(seq, libs, threshold=0.5, directionforward=True):
    """
    Match libs with the sequence
    """
    result = []
    for lib in tqdm(libs):
        pop = {}
        pop["library"] = lib["name"]
        # See algo1_lycopene for the parameter below in the template
        # threshold = lib["score_threshold"]
        # print('pop: ', pop)       
        # breakpoint()
        candidates = match_library(seq, Library(lib), threshold, directionforward)
        cl = []
        for candidate in candidates:
            for c in candidate:
                cl.append(
                    {
                        "name": c.name,
                        "score": c.score,
                        "start": c.start,
                        "length": c.length,
                        "end": c.end,
                    }
                )
        pop["candidates"] = cl
        result.append(pop)
    return result


def get_sequences(dir_dict):
    """
    Return list of sequences
    """

    SEQUENCES_EXTENSION = dir_dict["extension"]
    SEQUENCES_PATH = dir_dict["sequences_path"]
    seq_dir_names = dir_dict["seq_dir_names"]

    sequences = []
    for seq_dir in seq_dir_names:
        seqs = Path(path.join(SEQUENCES_PATH, seq_dir)).rglob(
            "*{0}".format(SEQUENCES_EXTENSION)
        )
        sequences.append(seqs)
    return sequences


def get_slices_libs(template):
    """
    Get slices libraries

    Args:
        template (dict): Template JSON data as a dict structure
    Returns:
        dict of slices libraries
    """

    slices_libs = {}
    for sli in template["template_slices"]:
        libs = []
        for pos in sli["template_slice"]:
            lib = template["template"]["structure"][pos - 1]["library_source"]
            libs.append(template["component_sources"][lib])
        slices_libs[sli["name"]] = libs
    return slices_libs


@timeit
def iter_all_seq(
    input_sequences,
    template_json_file,
    match_output_filename,
    reconstruction_output_filename,
    threshold=0.99,
):
    """
    Iterate over sequences

    Args:
        input_sequences (dict): Input dictionary with info about the input sequences:
        output_filename (str): Output filename

    Example:

    input_sequences = {
        'extension' = ".seq"
        'sequences_path' = "/data/Imperial/src/lyc-basic-ass-ind/"
        'seq_dir_names' = ["output"]
    }
    """

    # Get sequences to match
    sequences = get_sequences(input_sequences)

    # Get the filenames in a list and not this freakin generator
    seq_filenames = []
    for seq in sequences:
        for filename in seq:
            seq_filenames.append(filename)

    # Loop over the sequences
    r = []
    for filename in seq_filenames:
        sq = Sequence(filename)
        json_to_output = {}
        json_to_output["target"] = sq.name

        # Logging
        logging.info(f"Target sequence: {sq.name}")

        with open(template_json_file) as json_file:
            template = json.load(json_file)

        # Get libs from template
        template["template"]
        libs = get_slices_libs(template)
        libs_to_match = libs["construct"]  # name of the fake primer

        # Match sequence
        matches = match_libs(sq, libs_to_match, threshold=threshold)
        json_to_output["matches"] = matches
        r.append(json_to_output)

    # Write output result in JSON file
    with open(match_output_filename, "w") as filename:
        json.dump(r, filename, indent=2, separators=(",", ":"))


def match(template, threshold, overlap, match_results_path,directionforward, *targets):
    """
    Match
    """
    # Load JSON template
    with open(template) as json_file:
        template = json.load(json_file)
    r = []
    error_log = []
    # continue_reconstruct = False
    # print(targets, threshold)


    # Matching
    for target in targets:
        sq = Sequence(target, directionforward)
        # print(f'Direction 53: {direction53}, \n Sequence: {sq.sequence}')
        # breakpoint()
        json_to_output = {}
        json_to_output["target"] = sq.name
        print('FINDING MATCHES FOR: ',sq.name)
        libs = get_slices_libs(template)
        # print('libs:  ', libs)
        libs_to_match = libs["construct"]  # name of the fake primer
        # print('libs:  ', libs_to_match)
        
        matches = match_libs(sq, libs_to_match, threshold=threshold, directionforward=directionforward )
        # print(f'matches are {matches}')
        # continue_reconstruct = True  ## Only continue with reconstruction if we have identified each part
        # for match in matches:
        #     if match["candidates"]:
        #         json_to_output["matches"] = matches
        #         r.append(json_to_output)
        #         continue
        #     else:
        #         error_log.append(f'Match not found for part {match} with threshold ' + str(threshold))
        #         target_name = sq.name
        #         continue_reconstruct = False
        json_to_output["matches"] = matches
        r.append(json_to_output)
                
        
        # print('length of matches is: ', len(r)) 
    # breakpoint()   
    # s = json.dumps(r, indent=2, separators=(",", ":"))
    # total_results = []
    # if continue_reconstruct:
    try:
        print('Attempting reconstruct')
        print('length of input r:', len(r))


        # with open(f'template_seq_data/kl_constructs/Library1_5_7184/matching_outputs/Library1_5_7184_matching_data_0_9.json', 'w') as f:
        with open(match_results_path, 'w') as f:
            json.dump(r,f, indent=2, separators=(",", ":"))
        
        ##-------------COMMENTED OUT for no reconstruction--------------------    
        reconstruction_result, errors = reconstruct(r, overlap=overlap)
        # print(f'Reconstruction result: {reconstruction_result, errors}')
        if errors != []:
            error_log.append(errors)
        # print('error log: ',error_log)
        # total_results.append(reconstruction_result)
        print('length of reconstruction result: ', len(reconstruction_result))
        ss = json.dumps(reconstruction_result, indent=2, separators=(",", ":"))
        # print("ss", ss)
        ##---------------------------------------------
        # ss = json.dumps(r)
    except Exception as e:
        print('Unknown error: ', e)
        error_log.append(f'Unknown Error: {e}')
        ss = {}
        # ss = s
    # else:
    #     # ss = s
    #     failed_match_result = {
    #                 "target": 'failed reconstruction',
    #                 "reconstruct": None,
    #                 "score": 0,
    #                 "path": None,
    #             }
    #     total_results.append(failed_match_result)
    
    # ss = json.dumps(total_results, indent=2, separators=(",", ":"))
    errors_json = json.dumps(error_log, indent=2, separators=(",", ":"))

    return ss, errors_json


def remove_duplicates(result_json_str):
    # Ensure result_json is a Python list, not a string
    if isinstance(result_json_str, str):
        result_json = json.loads(result_json_str)  # Convert from string to Python list
    else:
        result_json = result_json_str

    unique_results = []
    seen = set()

    for entry in result_json:
        # Ensure 'path' is a list before processing

        if entry.get('path', None) is None:
            entry['score'] = 0

        if not isinstance(entry.get('path', []), list):
            continue  # Skip invalid entries

        # Convert 'path' to a tuple of tuples (to make it hashable)
        path_tuple = tuple(
            (p['name'], p['score'], p['start'], p['length'], p['end']) for p in entry['path']
        )

        # Create a hashable representation of the entry
        entry_tuple = (
            entry['target'],
            entry['reconstruct'],
            entry['score'],
            path_tuple
        )

        # If not seen, add to unique list and mark as seen
        if entry_tuple not in seen:
            seen.add(entry_tuple)
            unique_results.append(entry)

    return unique_results


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


@plac.pos("template", "JSON construct template. Example: consruct_template.json")
@plac.pos("threshold", "Threshold", type=float)
@plac.pos("overlap", "Overlap tolerance in bases", type=int)
@plac.pos("output_path", f"Output path for results parquet file", type=str)
@plac.pos("directionforward", f"Set True if sequence is in the forward direction", type=str2bool)
@plac.pos("match_results_path", f"Output path for match results json file", type=str)
@plac.pos("targets", f"Target sequence files. Example: Sanger008.seq", type=str)
def main(template, output_path, match_results_path, directionforward, threshold=0.7, overlap=0, *targets): # Hard coded threshold 
    """
    cMatch command line tool
    """
    st.set_page_config(layout="wide")
    # overlap_pct = 0
    

    start_time = time.time()

    
    output_dir = os.path.dirname(match_results_path)

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print(f'Number of input targets: {len(targets)} \n Overlap tolerance: ({overlap} bases), Direction Forward: {directionforward}')
    result, error_log = match(template, threshold, overlap, match_results_path, directionforward, *targets)
    # breakpoint()
    store_match_results(result, output_path,similarity_threshold= threshold, overlap_tolerance=f'{overlap}')

   # Plotting used for GFP 3-part construct
    # visualise_distribution(result, overlap, plot_individual_parts=True, plot_over_acc_levels=True)
    # plot_3d_multiple_scores(result, overlap, threshold)
    
    # General plotting
    # visualise_parts(result)
    # plot_error_types(error_log, overlap)
    
    execution_time = time.time() - start_time
    print(f'Execution Time: {execution_time:.4f} seconds')
    # print(result)



if __name__ == "__main__":
    plac.call(main)

import json
import itertools
from time import sleep, strftime
from os import path
from pprint import pprint
from futils import timeit, read_json

import logging
from statistics import geometric_mean


def compute_scores(paths):
    """
    Returns final score of the candidate pathway

    Arguments:
        paths list[str]

    Returns:
        list[float]  scores
    """
    scores = []
    for p in paths:
        gm = geometric_mean([e["score"] for e in p])
        scores.append(gm)
    return scores


def construct_names(paths):
    """ """
    names = []
    for p in paths:
        names.append("-".join([e["name"] for e in p]))
    return names


@timeit
def reconstruct(matches, overlap=50):
    """
    Reconstruction

    Args:
        matches (dict): JSON object

    Returns:
        list of dict containing the target, reconstruct, score and parts list
            ex: [ {
                    'target': 'vio-B0030-B0031-B0032-B0033-B0064',
                    'reconstruct': 'J23101-B0030-VioA-B0015-J23101-B0031-VioB-B0015-J23101-B0032-VioC-B0015-J23101-B0033-VioD-B0015-J23101-B0064-VioE-B0015',
                    'score': 20.0,
                    'path': [
                        {'name': 'J23101', 'score': 1.0, 'start': 4, 'length': 35, 'end': 39},
                        {'name': 'B0030', 'score': 1.0, 'start': 43, 'length': 15, 'end': 58},
                        {'name': 'VioA', 'score': 1.0, 'start': 62, 'length': 1293, 'end': 1355},
                        {'name': 'B0015', 'score': 1.0, 'start': 1359, 'length': 129, 'end': 1488},
                        {'name': 'J23101', 'score': 1.0, 'start': 1492, 'length': 35, 'end': 1527},
                        {'name': 'B0031', 'score': 1.0, 'start': 1531, 'length': 14, 'end': 1545},
                        {'name': 'VioB', 'score': 1.0, 'start': 1549, 'length': 3033, 'end': 4582},
                        {'name': 'B0015', 'score': 1.0, 'start': 4586, 'length': 129, 'end': 4715},
                        {'name': 'J23101', 'score': 1.0, 'start': 4719, 'length': 35, 'end': 4754},
                        {'name': 'B0032', 'score': 1.0, 'start': 4758, 'length': 13, 'end': 4771},
                        {'name': 'VioC', 'score': 1.0, 'start': 4775, 'length': 1326, 'end': 6101},
                        {'name': 'B0015', 'score': 1.0, 'start': 6105, 'length': 129, 'end': 6234},
                        {'name': 'J23101', 'score': 1.0, 'start': 6238, 'length': 35, 'end': 6273},
                        {'name': 'B0033', 'score': 1.0, 'start': 6277, 'length': 11, 'end': 6288},
                        {'name': 'VioD', 'score': 1.0, 'start': 6292, 'length': 1158, 'end': 7450},
                        {'name': 'B0015', 'score': 1.0, 'start': 7454, 'length': 129, 'end': 7583},
                        {'name': 'J23101', 'score': 1.0, 'start': 7587, 'length': 35, 'end': 7622},
                        {'name': 'B0064', 'score': 1.0, 'start': 7626, 'length': 12, 'end': 7638},
                        {'name': 'VioE', 'score': 1.0, 'start': 7642, 'length': 612, 'end': 8254},
                        {'name': 'B0015', 'score': 1.0, 'start': 8258, 'length': 129, 'end': 8387}
                        ]
                    }
                ]

    """
    # Read the JSON file with all the matches to reconstruct
    # targets = read_matches(matches)
   
    # Read the input list directly
    targets = matches
    print(f' length of input matches: {len(targets)}')
    target_reconstructions = []
    total_result = []
    total_errors = []

    # Reconstruct each target
    for target in targets:
        print("Target:", target["target"])
        libs = target["matches"]
        candidates = []
        result = []
        errors = []

        # Root
        paths = []
        if len(libs[0]["candidates"])==0:
            print(f'No candidate for part: {libs[0]["library"]}')
            d = {
                "target": target["target"],
                "reconstruct": 'failed reconstruction',
                "score": 0,
                "path": None,
                "errors": f'No candidate for part: {libs[0]["library"]}'
                }
            errors.append(d)
            print('breaking on lib[0] for target: ', target["target"] )
            
        else:
            for e in libs[0]["candidates"]:
                paths.append([e])
            # print("\tPAAAA", paths)

            #print(strftime("%Y%m%d-%H%M%S"))
            #print("Depth:", 0)
            #print("\tnb paths:", len(paths))

            for i in range(1, len(libs), 1):
                if len(libs[i]["candidates"])==0:
                    print(f'No candidate for part: {libs[i]["library"]}')
                    d = {
                        "target": target["target"],
                        "reconstruct": 'failed reconstruction',
                        "score": 0,
                        "path": None,
                        "errors": f'No candidate for part: {libs[i]["library"]}'
                        }
                    errors.append(d)
                    paths = [] # Discard incomplete paths if we have any parts with 0 matches
                    print(f'breaking on {libs[i]["library"]} lib for {target["target"]}')
                    break
                else:
                # Add new lib
                    np = []
                    for pa in paths:
                        #print(libs[i]['candidates'])
                        aa = sorted(
                            libs[i]["candidates"], key=lambda d: d["score"], reverse=True
                        )
                        #aa = aa[0:1]
                        #print("aa:", aa)
                        # TODO verify highest score
                        for e in aa:
                            new = pa.copy()
                            new.append(e)
                            np.append(new)
                    # pprint(f'NP: {np}')
                    # Prune
                    paths = []

                    # print("\nDepth:", i)
                    # print("\tnb paths:", len(np))
                    
                    for p in np:
                        # print("Path:", p)
                        # print(p[i - 1]["end"], p[i]["start"])
                        if p[i - 1]["end"] <= p[i]["start"] + overlap:
                            # print("\tADDDDING:", p)
                            paths.append(p)
                        # else:
                            # if i == 3:
                                # print(f'Constructs {p[i-1]["name"]} and {p[i]["name"]} overlap by {p[i - 1]["end"] - p[i]["start"]} bases ')
                                # errors.append(f'Constructs {p[i-1]["name"]} and {p[i]["name"]} overlap by {p[i - 1]["end"] - p[i]["start"]} bases ')
                    # print('path number: ', len(paths))
                    # Define result for reconstruction failures due to overlaps
                    if paths==[]:
                        d = {
                        "target": target["target"],
                        "reconstruct": 'failed reconstruction',
                        "score": 0,
                        "path": None,
                        "errors": 'Bases Overlapping or order is wrong'
                        }
                        errors.append(d)
                        print('Error logged for target: ', target['target'])
                        print(' breaking on overlaps for: ', target["target"])
                        break
                        
                #print("\tafter pruning:", len(paths))
            print('computing scores for target: ', target['target'])
            scores = compute_scores(paths)
            names = construct_names(paths)
            # print(f'paths: {paths}')

        r = []
        if paths!=[]:
            # errors = [] # Clear any existing errors from broken paths
            print('target: ', target['target'])
            for i in range(len(paths)):
                # print('path found for target: ', target['target'])
                d = {
                    "target": target["target"],
                    "reconstruct": names[i],
                    "score": scores[i],
                    "path": paths[i],
                    "errors": None
                }
                r.append(d)
            target_reconstructions.append(r)
            
            # print(f"target reconstructions {target_reconstructions}")
            rep = []
            for rr in target_reconstructions:
                w = sorted( rr, key=lambda d: d["score"], reverse=True)
                # print(w)
                rep.append(w[0])
                print('ADDING PATH')
            total_result += rep # record any failed matching/reconstruction

        else:
                # rep=[]
                # d = {
                #     "target": target["target"],
                #     "reconstruct": 'failed reconstruction',
                #     "score": 0,
                #     "path": None,
                #     "errors": errors
                #     }
                # r.append(d)
                # rep.append(r)
            total_result += errors
            total_errors += errors
           
            print('No reconstruction for target: ', target['target'])
    return total_result, total_errors    


def main():
    """
    Main
    """
    # Logging configuration
    current_file = path.basename(__file__).split(".")[0]
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s: %(message)s",
        filename=f"logs/{current_file}.log",
        encoding="utf-8",
        level=logging.DEBUG,
    )

    TEMPLATE = "/data/Imperial/src/matching/templates/template_violacein_02.json"
    RES_DIR = "/data/Imperial/src/matching/output_results/"
    RES = "matching-results-run_algo1-2-targets-template-run-0-20210804-130134.json"
    MATCHES = path.join(RES_DIR, RES)
    #TEMPLATE = "/data/Imperial/src/matching/templates/template_lycopene_sanger.json"
    #RES_DIR = "/data/Imperial/src/matching/output_results/"
    #RES = "20210807-185353-matching-results-run_cm2_2-cm2-lycopene-1target-UTR1-RBS-A12-UTR2-RBS-A12-UTR3-RBS-A12-CrtI-th05-run-1-from-1.json"
    #MATCHES = path.join(RES_DIR, RES)

    r = reconstruct(read_json(MATCHES))
    pprint(r)



if __name__ == "__main__":
    main()

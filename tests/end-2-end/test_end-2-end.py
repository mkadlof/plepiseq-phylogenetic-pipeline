import json
from pathlib import Path
import os
import pytest
from ete3 import Tree
import json, functools, requests
import fastjsonschema
# following test are performed
# 1. check if output json file passes the schema
# 2. check if all the files found in the json exist
# 3. check randomly selected values from the script
# 4. check if trees in .nwk files have an expected topology
# 5. verify md5 sum of microreact project /can't calculate md5sum there is a timestamp, we test blob for csv"

@functools.lru_cache(maxsize=1)
def _load_schema_validator(schema_arg: str | None):
    if schema_arg is None:
        pytest.skip("No --schema provided; skip schema validation")
    if schema_arg.startswith(("http://", "https://")):
        r = requests.get(schema_arg, timeout=30); r.raise_for_status()
        schema = r.json()
    else:
        schema = json.loads(Path(schema_arg).read_text(encoding="utf-8"))
    return fastjsonschema.compile(schema)

GOLDENS = {
    "test_sars_MN908947.3_filogram.nwk" : "(SARS3_01:0.000165683,(SARS3_07:0.000145298,(SARS3_15:3.37883e-05,SARS3_16:2.5259e-06,(SARS3_10:0,SARS3_17:0,SARS3_18:0)100:2.3619e-06)100:0.000259306)98:0.000533203,(((SARS3_02:2.5259e-06,SARS3_04:3.43302e-05,(SARS3_09:2.5259e-06,SARS3_19:2.5259e-06)97:6.77818e-05,SARS3_06:3.39058e-05,(SARS3_03:0,SARS3_20:0)100:2.5259e-06)98:0.000169284,SARS3_11:0.000136175)100:0.00097618,SARS3_14:0.00238676)100:0.00124936);",
    "test_sars_MN908947.3_chronogram.nwk": "(SARS3_14:2.77687,((SARS3_01:2.49018,(SARS3_07:1.51807,(SARS3_15:0.00178,SARS3_16:0.00178,SARS3_10:0.00178,SARS3_17:0.00178,SARS3_18:0.00178)NODE_0000002:0.04779)NODE_0000001:0.06801)NODE_0000000:0.44558,(SARS3_11:0.16641,(SARS3_02:0.00887,SARS3_04:0.00887,SARS3_06:0.00887,SARS3_03:0.00887,SARS3_20:0.00887,(SARS3_09:0.00156,SARS3_19:0.00156)NODE_0000007:0.00731)NODE_0000006:0.15753)NODE_0000005:1.85977)NODE_0000004:0.03289)NODE_0000003:0.00100;",
    "test_sars_MN908947.3_microreactproject.microreact": "data:application/octet-stream;base64, c3RyYWluCXZpcnVzCWRhdGUJY291bnRyeQljaXR5CXN0YXR1c19BCXR5cGUJbGF0aXR1ZGUJbG9uZ2l0dWRlCXllYXIJbW9udGgJZGF5ClNBUlMzXzAxCXNhcnMtY292LTIJMjAyMy0xMS0yOQlQb2xza2EJQnlkZ29zemN6CUEJc2Fycy1jb3YtMgk1My4xMjE5NjQ4CTE4LjAwMDI1MjkJMjAyMwkxMQkyOQpTQVJTM18wMglzYXJzLWNvdi0yCTIwMjMtMDEtMDEJUG9sc2thCU9wb2xlCUEJc2Fycy1jb3YtMgk1MC42NjY4MTg0CTE3LjkyMzY0MDgJMjAyMwkxCTEKU0FSUzNfMDMJc2Fycy1jb3YtMgkyMDIzLTAxLTAxCU5pZW1jeQlLw7ZsbglBCXNhcnMtY292LTIJNTAuOTM4MzYxCTYuOTU5OTc0CTIwMjMJMQkxClNBUlMzXzA0CXNhcnMtY292LTIJMjAyMy0wMS0wMQlDemVjaHkJUGlsem5vCUIJc2Fycy1jb3YtMgk0OS43NDc3NDE1CTEzLjM3NzUyNDkJMjAyMwkxCTEKU0FSUzNfMDUJc2Fycy1jb3YtMgkyMDIzLTAxLTAxCVBvbHNrYQlLcmFrw7N3CUIJc2Fycy1jb3YtMgk1MC4wNjE5NDc0CTE5LjkzNjg1NjQJMjAyMwkxCTEKU0FSUzNfMDYJc2Fycy1jb3YtMgkyMDIzLTAxLTAxCU5pZW1jeQlCZXJsaW4JQglzYXJzLWNvdi0yCTUyLjUxNzM4ODUJMTMuMzk1MTMwOQkyMDIzCTEJMQpTQVJTM18wNwlzYXJzLWNvdi0yCTIwMjMtMDEtMDMJUG9sc2thCVN6Y3plY2luCUEJc2Fycy1jb3YtMgk1My40MzAxODE4CTE0LjU1MDk2MjMJMjAyMwkxCTMKU0FSUzNfMDgJc2Fycy1jb3YtMgkyMDIzLTAxLTExCUN6ZWNoeQlCcm5vCUIJc2Fycy1jb3YtMgk0OS4xOTIyNDQzCTE2LjYxMTMzODIJMjAyMwkxCTExClNBUlMzXzA5CXNhcnMtY292LTIJMjAyMy0wMS0wMQlDemVjaHkJUGFyZHViaWNlCUEJc2Fycy1jb3YtMgk1MC4wMzg1ODEyCTE1Ljc3OTEzNTYJMjAyMwkxCTEKU0FSUzNfMTAJc2Fycy1jb3YtMgkyMDIxLTA3LTE2CU5pZW1jeQlGcmFua2Z1cnQJQQlzYXJzLWNvdi0yCTUwLjExMDY0NDQJOC42ODIwOTE3CTIwMjEJNwkxNgpTQVJTM18xMQlzYXJzLWNvdi0yCTIwMjMtMDEtMDEJUG9sc2thCcWBw7NkxboJQglzYXJzLWNvdi0yCTUxLjc2ODczMjMJMTkuNDU2OTkxMQkyMDIzCTEJMQpTQVJTM18xMglzYXJzLWNvdi0yCTIwMjMtMDEtMDEJQ3plY2h5CVByYWdhCUEJc2Fycy1jb3YtMgk1MC4wODc0NjU0CTE0LjQyMTI1MzUJMjAyMwkxCTEKU0FSUzNfMTMJc2Fycy1jb3YtMgkyMDI0LTAxLTAxCU5pZW1jeQlIYW1idXJnCUIJc2Fycy1jb3YtMgk1My41NTAzNDEJMTAuMDAwNjU0CTIwMjQJMQkxClNBUlMzXzE0CXNhcnMtY292LTIJMjAyMy0wOS0yMAlQb2xza2EJV3JvY8WCYXcJQQlzYXJzLWNvdi0yCTUxLjEwODk3NzYJMTcuMDMyNjY4OQkyMDIzCTkJMjAKU0FSUzNfMTUJc2Fycy1jb3YtMgkyMDIxLTA3LTE2CVBvbHNrYQlHZGHFhHNrCUEJc2Fycy1jb3YtMgk1NC4zNDgyOTA3CTE4LjY1NDAyMzMJMjAyMQk3CTE2ClNBUlMzXzE2CXNhcnMtY292LTIJMjAyMS0wNy0xNglQb2xza2EJS2F0b3dpY2UJQQlzYXJzLWNvdi0yCTUwLjI1OTg5ODcJMTkuMDIxNTg1MgkyMDIxCTcJMTYKU0FSUzNfMTcJc2Fycy1jb3YtMgkyMDIxLTA3LTE2CU5pZW1jeQlEcmV6bm8JQQlzYXJzLWNvdi0yCTUxLjA0OTMyODYJMTMuNzM4MTQzNwkyMDIxCTcJMTYKU0FSUzNfMTgJc2Fycy1jb3YtMgkyMDIxLTA3LTE2CUN6ZWNoeQlPc3RyYXdhCUEJc2Fycy1jb3YtMgk0OS44MzQ5MTM5CTE4LjI4MjAwODQJMjAyMQk3CTE2ClNBUlMzXzE5CXNhcnMtY292LTIJMjAyMy0wMS0wMQlOaWVtY3kJTW9uYWNoaXVtCUEJc2Fycy1jb3YtMgk0OC4xMzcxMDc5CTExLjU3NTM4MjIJMjAyMwkxCTEKU0FSUzNfMjAJc2Fycy1jb3YtMgkyMDIzLTAxLTAxCVBvbHNrYQlUb3J1xYQJQQlzYXJzLWNvdi0yCTUzLjAxMDI3MjEJMTguNjA0ODA5NAkyMDIzCTEJMQo=",
    'test_sars.json': {
        "output"  : {
            "input_params_data" : {
                "input_ids": [
                "SARS3_01",
                "SARS3_02",
                "SARS3_03",
                "SARS3_04",
                "SARS3_05",
                "SARS3_06",
                "SARS3_07",
                "SARS3_08",
                "SARS3_09",
                "SARS3_10",
                "SARS3_11",
                "SARS3_12",
                "SARS3_13",
                "SARS3_14",
                "SARS3_15",
                "SARS3_16",
                "SARS3_17",
                "SARS3_18",
                "SARS3_19",
                "SARS3_20"
            ],
            "phylogenetic_min_support": 0.75
            },
            "chronogram_data" : {"MN908947.3": {
                "clockrate_correlation": 0.3
            }
            },
            "sequence_filtering_data": {
                "MN908947.3": {
                    "SARS3_01" : {"number_of_N": 126, "number_of_ambiguous": 0, "status": "tak",},
                    "SARS3_03" : {"number_of_N": 307, "number_of_ambiguous": 0, "status": "tak",},
                    "SARS3_05" : {"number_of_N": 23340, "number_of_ambiguous": 0,"status": "nie",},
                    "SARS3_08": {"number_of_N": 121, "number_of_ambiguous": 26,"status": "nie"}
                }
            },
            "sequence_clustering_data": {
                "MN908947.3": {"threshold": 1.0,  "clusters": {"SARS3_03": ["SARS3_03","SARS3_20"],
                                                               "SARS3_02": ["SARS3_02"]
                                                               }
                               }
            },
            "filogram_data": {"MN908947.3": { "id_filogram": ["SARS3_01",
                                                              "SARS3_07",
                                                              "SARS3_10",
                                                              "SARS3_15",
                                                              "SARS3_16",
                                                              "SARS3_02",
                                                              "SARS3_03",
                                                              "SARS3_04",
                                                              "SARS3_09",
                                                              "SARS3_19",
                                                              "SARS3_06",
                                                              "SARS3_11",
                                                              "SARS3_14"],
                                              "program_name": "iqtree2",
                                              "phylogenetic_starting_trees": 10
                                              }
                              }
            }
    },
    'test_influenza.json': {

    }
}


def load_json_content(json_path: Path):
    with open(json_path, 'r') as f:
        return json.load(f)


def test_check_json_validity(json_file, request):

    # read json
    content = load_json_content(json_file)

    # read schema from repo
    validate = _load_schema_validator(request.config.getoption("schema"))

    # evaluate content against schema
    try:
        validate(content)
        assert True == True
    except Exception as e:
        assert False == True,  f"{json_file.name}: {e}"


def test_directory_existence(json_file):
    content = load_json_content(json_file)
    results_dir = content.get('output', {}).get("input_params_data", {}).get("results_dir", "") or ""
    exec_dir = content.get('output', {}).get("ExecutionDir_dir", "") or ""
    print(results_dir)
    if not results_dir:
        assert False, f"{json_file.name}: no results dir found"
    if not exec_dir:
        assert False, f"{json_file.name}: no execution dir found"

    assert True


@pytest.mark.parametrize("json_field",
                         ["filogram_nwk",
                          "chronogram_nwk",
                          "microreact_json"
                          ])
def test_files_exist(json_file, json_field):
    status = True
    content = load_json_content(json_file)
    exec_dir = content.get('output', {}).get("ExecutionDir_dir", "") or ""

    files_dict = content.get("output", {}).get(json_field, {}) or {}
    if len(files_dict) == 0:
        assert False, f"{json_file.name}: no data found for {json_field}"

    for segment, path in files_dict.items():
        segment_file = Path(exec_dir) / f"{path}"
        if not os.path.isfile(segment_file):
            status = False
            break

    if status:
        assert True
    else:
        assert False, f"{json_file.name}: no {json_field} file found for segment {segment}"


def test_input_param_ids(json_file):

    content = load_json_content(json_file)
    observed = set(content["output"]["input_params_data"]["input_ids"])

    expected = set(GOLDENS[json_file.name]["output"]["input_params_data"]["input_ids"])

    assert observed == expected, f"{json_file.name}: input params ids mismatch"

def test_input_param_min_suuport(json_file):

    content = load_json_content(json_file)

    obsered = content["output"]["input_params_data"]["phylogenetic_min_support"]
    expected =  GOLDENS[json_file.name]["output"]["input_params_data"]["phylogenetic_min_support"]


    assert  obsered == expected,   f"{json_file.name}: input params min support mismatch"

def test_chronogram_data(json_file):

    content = load_json_content(json_file)
    observed = content["output"]["chronogram_data"]["MN908947.3"]["clockrate_correlation"]
    expected =  GOLDENS[json_file.name]["output"]["chronogram_data"]["MN908947.3"]["clockrate_correlation"]
    assert expected == observed, f"{json_file.name}: clockrate_correlation mismatch"


@pytest.mark.parametrize("sample",
                         ["SARS3_01",
                          "SARS3_03",
                          "SARS3_05",
                          "SARS3_08"
                          ])
def test_sequence_filtering_data(json_file, sample):

    content = load_json_content(json_file)

    observed = content["output"]["sequence_filtering_data"]["MN908947.3"][sample]

    expected =  GOLDENS[json_file.name]["output"]["sequence_filtering_data"]["MN908947.3"][sample]

    for key in expected.keys():
        assert expected[key] == observed[key], f"{json_file.name}: {key} mismatch in filtering data"


@pytest.mark.parametrize("sample",
                         ["SARS3_03",
                          "SARS3_02"
                          ])
def test_sequence_clustering_data(json_file, sample):

    content = load_json_content(json_file)
    observed = set(content["output"]["sequence_clustering_data"]["MN908947.3"]["clusters"][sample])
    expected =  set(GOLDENS[json_file.name]["output"]["sequence_clustering_data"]["MN908947.3"]["clusters"][sample])

    assert observed == expected,  f"{json_file.name} mismatch in clustering data for sample {sample}"



@pytest.mark.parametrize("json_field",
                         ["program_name",
                          "phylogenetic_starting_trees"
                          ])
def test_filogram_data_ids(json_file, json_field):

    content = load_json_content(json_file)
    observed = content["output"]["filogram_data"]["MN908947.3"][json_field]
    expected =  GOLDENS[json_file.name]["output"]["filogram_data"]["MN908947.3"][json_field]

    if isinstance(observed, list):
        observed = set(observed)
        expected = set(expected)

    assert observed == expected,  f"{json_file.name} mismatch in {json_field} in filogram_data"


def test_tree_topology(tree_file):
    # We allow 1 different split in trees
    expected = Tree(GOLDENS[tree_file.name], format=1)
    # observed = Tree(open(tree_file, "r").readline(), format=1)
    observed = Tree(Path(tree_file).read_text(encoding="utf-8"), format=1)


    rf, rf_max, *_ = expected.robinson_foulds(observed, unrooted_trees=True)
    assert rf <= 1, f"{tree_file.name} mismatch with expected tree"


def test_microreact_blob(microreact_file):
    content = load_json_content(microreact_file)

    expected = GOLDENS[microreact_file.name]
    observed =  content["files"]["sib4"]["blob"]


    assert observed == expected, f"Error in blo blob csv in microreact file {microreact_file.name}"
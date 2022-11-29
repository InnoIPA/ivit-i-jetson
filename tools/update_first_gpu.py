#!/usr/bin/python3
import json, os, sys, argparse
sys.path.append(os.getcwd())
from ivit_i.utils.devices import get_device_info

def def_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--framework", default="tensorrt", help="framework [ tensorrt, openvino ]")
    parser.add_argument("-j", "--json", help="path to task configuration")
    args = parser.parse_args()

    return args

if __name__ == "__main__":

    print("# Modify GPU Information to each configuration \n")
    
    # Define Argument
    args            = def_args()
    
    task_cfg_path   = args.json
    framework       = args.framework
    
    # Define Variable Placefolder
    task_cfg, model_cfg_path, model_cfg = None, None, None

    # Get Task Configuration and Get Model Config Path
    with open(args.json, 'r') as f:
        task_cfg = json.load(f)
        model_cfg_path = task_cfg["prim"]["model_json"]

        if None in [ task_cfg, model_cfg_path]:
            raise Exception("Parse json failed ... ")

    # Open Model Configuration
    with open(model_cfg_path, "r") as f:
        model_cfg = json.load(f)
        
        if None in [ model_cfg ]:
            raise Exception("Parse model json failed ... ")
        
        # Get First GPU and Update
        first_device_name = list(get_device_info().keys())[0]
        model_cfg[framework]["device"] = first_device_name
        print("Detected GPU: {}".format(first_device_name))

    # Write Into File ( Model Config )
    with open(model_cfg_path, "w") as f:
        json.dump(model_cfg, f, ensure_ascii=False, indent=4)
import os
from typing import Dict, List
import ipdb

def main():
    must_gather_path:str = "/home/jpeimer/Downloads/must-gather-cnv"
    all_yaml_files:Dict[str,List[str]] = {}
    all_log_files: Dict[str, List[str]] = {}
    for root, dirs, files in os.walk(must_gather_path):
        for _dir in dirs:
            for _file in os.listdir(os.path.join(root, _dir)):
                file_extention = _file.rsplit(".",1)
              #  print(f"{_file=}, {file_extention[-1]=}")
                if file_extention[-1] in ("yaml", "yml"):
                    # print(os.path.join(root, _dir, _file))
                    all_yaml_files.setdefault(os.path.join(root, _dir),[]).append(_file)

                # Poa may have several containers, the path to the log is:
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kubecfg-setup/kubecfg-setup/logs
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kube-rbac-proxy-node/kube-rbac-proxy-node/logs
                elif file_extention[-1] == "log":
                    all_log_files.setdefault(os.path.join(root, _dir),[]).append(_file)



    # Todo: fill dictionaries for all files kinds

    ipdb.set_trace()



if __name__ == "__main__":
    main()

# Must-gather explorer

Explore the collected must-gather data

## Prerequisite

Install [uv](https://github.com/astral-sh/uv)

## Installation

```bash
uv tool install must-gather-explorer
```

After successful installation, these CLI tools will be available:

- must-gather-explorer
- must-gather-explorer-update-aliases

## How to use

- Run the command:

To run with debug logs pass `-v`/`--verbose` flag.

```bash
must-gather-explorer --path=<path-to-must-gather-folder>
```

Once you executed the command, you will enter the must-gather-explorer shell `Enter the command:`, where you can prompt these commands:

- Get the resources:

```bash
get <resource_kind:mandatory> <resource_name_starts_with:optional> -n <namespace_name:optional>
```

- Example:

```bash
get Node # To get all Nodes
get PersistentVolumeClaim hpp # To get all PVCs when name starts from 'hpp'
get pvc hpp -n openshift-storage  # To get all PVCs in 'openshift-storage' namespace when name starts from 'hpp'
```

- To print the resource YAML, add `-oyaml` to the `get` command, for example:

```bash
get pvc hpp -oyaml # To print yamls of all PVCs when name starts from 'hpp'
get pvc hpp -n openshift-storage  -oyaml # To print yamls of all PVCs in 'openshift-storage' namespace when name starts from 'hpp'
```

- To print specific YAML fields, add `-f .<key>.<key>.<key>...` after `-oyaml`:

```bash
get node <node-name> -oyaml -f .status.nodeInfo
get pvc <pvc-name-start-with> -oyaml -f .spec.storageClassName # To print .spec.storageClassName of all PVCs when name starts from <pvc-name-start-with>
get pvc <pvc-name-start-with> -n <namespace>  -oyaml -f .spec.accessModes # To print .spec.accessModes of all PVCs in 'namespace' when name starts from <pvc-name-start-with>
```

- Help:

```bash
help
help get
```

- Exit:

```bash
exit
```

## Update cluster resources aliases

- Need to be logged-in to the OpenShift cluster or have exported KUBECONFIG
- Run the command:

```bash
must-gather-explorer-update-aliases
```

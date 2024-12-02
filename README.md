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
get -k <resource_kind:mandatory> -n <namespace_name:optional> --name <resource_name_starts_with:optional>
```

- Example:

```bash
get -k Node # To get all Nodes
get -k PersistentVolumeClaim --name hpp # To get all PVCs when name starts from 'hpp'
get -k pvc -n openshift-storage --name hpp # To get all PVCs in 'openshift-storage' namespace when name starts from 'hpp'
```

- To print the resource YAML, add `-oyaml` to the `get` command, for example:

```bash
get -k pvc --name hpp -oyaml # To print yamls of all PVCs when name starts from 'hpp'
get -k pvc -n openshift-storage --name hpp -oyaml # To print yamls of all PVCs in 'openshift-storage' namespace when name starts from 'hpp'
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

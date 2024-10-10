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

```bash
must-gather-explorer --path=<path-to-must-gather-folder>
```

Once you executed the command, you will enter the must-gather-explorer shell `Enter the command:`, where you can prompt these commands:

- Get the resources:

```bash
get <resource_kind:mandatory> <-n namespace_name:optional> <resource_name_starts_with:optional>
```

- Example:

```bash
get Node # To get all Nodes
get PersistentVolumeClaim hpp # To get all PVCs that name starts form 'hpp'
get PersistentVolumeClaim -n openshift-storage hpp # To get all PVCs in 'openshift-storage' namespace that name starts form 'hpp'
```

- Help:

```bash
help
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

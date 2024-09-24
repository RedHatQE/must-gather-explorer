# Must-gather explorer
Will help you to navigate the collected must-gather

## How to use
- Run the command:

```bash
poetry run must-gather-explorer --path=<path-to-must-gather-folder>
```
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
- Exit:
```bash
exit
```

## Update cluster resources aliases
- You need a live OpenShift cluster
- Run this command:

```bash
poetry run update-resources-aliases
```

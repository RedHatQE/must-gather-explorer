# Must-gather explorer
Will help you to navigate the collected must-gather

## How to use
- Install pipx
```bash
git clone https://github.com/RedHatQE/must-gather-explorer.git
cd must-gather-explorer
pipx install .
```
- Run the command:
```bash
must-gather-explorer --path=<path-to-must-gather-folder>
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
- Install pipx (see the instructions above)
- Run the command:

```bash
update-resources-aliases
```

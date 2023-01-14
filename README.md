# azure-devops-bulk-workitems

Create new workitems from a pre-defined list and assign them to a specific sprint.

## Setup

1. create the config.yaml file (see config.sample.yaml)
2. create the workitems.yaml file (see workitems.sample.yaml)
3. run the main.py Python script

## config.yaml file

This file contains the general configuration parameters used to connect to your Azure DevOps environment.

Make sure you get a personal access token first!

```yaml
organization: 'myAzureOrganization'
project: 'MyProjectName'
url: 'https://dev.azure.com/myAzureOrganization'
token: 'myPersonalAccessToken'
```

## workitems.yaml file

This file contains details for each work item that will be created. Multiple YAML documents can be put in this file, each delimited by **---** (three dashes).

The following fields are currently supported:
- type: work item type
- title
- assigned: assigned to
- area
- iteration
- description (supports formatting such as \<div\> for new line)

```yaml
type: Issue
title: test 1
area: myArea
iteration: myArea\2301
assigned: John Doe
description: test item 1
---
type: Issue
title: test 2 multiple lines
area: myArea
iteration: myArea\2301
description: line 1 in item 2<div>
  line 2 in item 2<div>
  line 3 in item 2
---
type: Issue
title: test 3
area: myArea
iteration: myArea\2301
description: test item 3
```

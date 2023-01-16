import yaml
from azure.devops.connection import Connection
from azure.devops.released.work_item_tracking import JsonPatchOperation
from msrest.authentication import BasicAuthentication

SIMULATION_ONLY = False


def get_patch_operation(op, path, value):
    patch_operation = JsonPatchOperation()
    patch_operation.op = op
    patch_operation.path = path
    patch_operation.value = value
    return patch_operation


def get_patch_oper(op, field, value):
    path = '/fields/{field}'.format(field=field)
    return get_patch_operation(op=op, path=path, value=value)


def get_link_patch_oper(op, parent_item):
    value = {"rel": "System.LinkTypes.Hierarchy-Reverse",
             "url": parent_item.url}
    return get_patch_operation(op=op, path='/relations/-', value=value)


if __name__ == '__main__':
    # get configuration
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    try:
        personal_access_token = config['token']
        organization_url = config['url']
        config_organization = config['organization']
        config_project = config['project']
        config_area = config['area']
        config_iteration = config['iteration']
    except KeyError:
        print("Error: missing item in configuration file")
        exit(1)

    # Create a connection to the org and get a client
    # the "core" client provides access to projects, teams, etc
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)
    core = connection.clients.get_core_client()
    client = connection.clients.get_work_item_tracking_client()

    # check if project exists
    project = core.get_project(config_project, include_capabilities=False, include_history=False)
    if project is None:
        print(f"Error: project not found: {config_project}")
        exit(1)

    # load list of new workitems
    with open('workitems.yaml', 'r') as workitems_file:
        docs = yaml.safe_load_all(workitems_file)

        for doc in docs:
            work_item_type = doc.get('type')
            title = doc.get('title')
            assigned = doc.get('assigned')
            description = doc.get('description')
            tasks = doc.get('tasks')

            print(f"-> Creating: [{work_item_type}] {title}")

            # check if we have a valid work item type
            if client.get_work_item_type(config_project, work_item_type) is None:
                print(f"Error: work item type not found: {work_item_type}")
                exit(1)

            # prepare payload for new work item creation
            patch_document = []
            if title is not None:
                patch_document.append(get_patch_oper('add', 'System.Title', title.strip()))
            if description is not None:
                patch_document.append(get_patch_oper('add', 'System.Description', description))
            if config_area is not None:
                patch_document.append(get_patch_oper('add', 'System.AreaPath', config_area.strip()))
            if config_iteration is not None:
                patch_document.append(get_patch_oper('add', 'System.IterationPath', config_iteration.strip()))
            if assigned is not None:
                patch_document.append(get_patch_oper('add', 'System.AssignedTo', assigned.strip()))

            # create new work item
            item = client.create_work_item(patch_document,
                                           config_project,
                                           work_item_type,
                                           validate_only=SIMULATION_ONLY,
                                           bypass_rules=False,
                                           suppress_notifications=True,
                                           expand=None)

            if tasks is not None:
                for task in tasks:
                    print(f"    --> task: {task}")
                    # prepare payload for subtask
                    task_document = [get_patch_oper('add', 'System.Title', task.strip())]
                    if config_area is not None:
                        task_document.append(get_patch_oper('add', 'System.AreaPath', config_area.strip()))
                    if config_iteration is not None:
                        task_document.append(get_patch_oper('add', 'System.IterationPath', config_iteration.strip()))
                    # link parent
                    task_document.append(get_link_patch_oper('add', item))
                    # create task, linked to parent
                    task_item = client.create_work_item(task_document,
                                                        config_project,
                                                        "Task",
                                                        validate_only=SIMULATION_ONLY,
                                                        bypass_rules=False,
                                                        suppress_notifications=True,
                                                        expand=None)

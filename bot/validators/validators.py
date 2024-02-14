def list_tasks_in_str(tasks_title: list) -> str:
    if len(tasks_title) == 0:
        return False
    string = ''
    last_task = tasks_title[-1]
    for task in tasks_title:
        if task == last_task:
            string += f'• {task}'
        else:
            string += f'• {task}\n'

    return string


def task_title_length_validator(title):
    if len(title) > 128:
        return False
    return True

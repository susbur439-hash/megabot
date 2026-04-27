def extract_task(data):
    """
    ЕДИНАЯ точка получения task
    ВСЯ система должна брать task только отсюда
    """

    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        task = data.get("task")

        if isinstance(task, str):
            return task

        return str(data)

    return str(data)


def normalize_task(task):
    """
    Безопасная нормализация task
    """

    if not isinstance(task, str):
        task = str(task)

    return task.strip().lower()

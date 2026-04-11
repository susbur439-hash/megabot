import os
import importlib.util


def run(data):
    project_root = "."
    system_map = {
        "files": [],
        "modules": [],
        "errors": [],
        "connections": []
    }

    # 📁 обход файлов
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                system_map["files"].append(full_path)

                # 🧠 проверка импорта
                try:
                    spec = importlib.util.spec_from_file_location("mod", full_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        system_map["modules"].append(file)

                        # 🔗 проверка функции run
                        if hasattr(module, "run"):
                            system_map["connections"].append({
                                "module": file,
                                "has_run": True
                            })
                        else:
                            system_map["connections"].append({
                                "module": file,
                                "has_run": False
                            })

                except Exception as e:
                    system_map["errors"].append({
                        "file": full_path,
                        "error": str(e)
                    })

    # 📊 статистика
    data["system_map"] = system_map

    data.setdefault("log", []).append(
        f"👁 observer: files={len(system_map['files'])} "
        f"modules={len(system_map['modules'])} "
        f"errors={len(system_map['errors'])}"
    )

    return data

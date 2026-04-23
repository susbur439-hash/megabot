class ControlGate:

    def check(self, decision, task_plan=None, goal=None):

        # 🔴 блок хаотичных модулей
        if decision == "create_module":

            if not task_plan:
                return {
                    "allowed": False,
                    "forced_decision": "task_interpreter",
                    "reason": "no task plan"
                }

            if not goal:
                return {
                    "allowed": False,
                    "forced_decision": "task_interpreter",
                    "reason": "no goal"
                }

        return {
            "allowed": True,
            "decision": decision
        }

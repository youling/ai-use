"""Static Role Model V2 invariants; these do not prove runtime Foreman behavior."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ForemanContractTests(unittest.TestCase):
    def test_one_foreman_role_and_legacy_modes(self):
        c = source("CONSTITUTION.md")
        r = source("20_ROLES/FOREMAN.md")
        self.assertIn("**Foreman（工头）**", c)
        self.assertIn("**Subagent（子执行上下文）**", c)
        self.assertIn("工头只有一种角色", r)
        self.assertIn("不设“主工头”", r)
        self.assertIn("历史 Builder / Research / Repair / Verifier", r)

    def test_child_is_not_parent_acceptance(self):
        r = source("20_ROLES/FOREMAN.md")
        i = source("docs/AGENT_INTERFACE.md")
        self.assertIn("CHILD_TERMINAL != FOREMAN_TERMINAL != ARCHITECT_ACCEPTANCE", r)
        self.assertIn("ATTEMPT_TERMINAL != WORK_CLOSED", r)
        self.assertIn("子对话 `SUCCESS`", i)
        self.assertIn("PREMATURE_YIELD", i)
        self.assertIn("可审阅 PR", r)

    def test_child_delegation_does_not_expand_authority(self):
        i = source("docs/AGENT_INTERFACE.md")
        r = source("30_PROTOCOLS/RECOVERY_HANDOFF.md")
        role = source("20_ROLES/FOREMAN.md")
        self.assertIn("FOREMAN_FIRST_LEVEL_SUBAGENT = WITHIN_DELEGATED_WORK", r)
        self.assertIn("NESTED_SUBAGENT_DEFAULT = DENY", r)
        self.assertIn("独立 child Work Coordinate", i)
        self.assertIn("fresh independent verification context", role)
        self.assertIn("不获得 Architect merge", role)

    def test_transport_is_not_durable_truth_or_wake_proof(self):
        role = source("20_ROLES/FOREMAN.md")
        i = source("docs/AGENT_INTERFACE.md")
        self.assertIn("Actions 不必是 Agent 消息总线", role)
        self.assertIn("GitHub 仍是 durable truth", i)
        self.assertIn("不证明外部 Foreman", role)

    def test_navigation_and_historical_compatibility(self):
        self.assertIn("Foreman Role Contract", source("README.md"))
        self.assertIn("Role Contract", source("40_GUIDES/ASYNC_FOREMEN.md"))
        self.assertIn("历史 Work Order", source("docs/AGENT_INTERFACE.md"))


    def test_architect_discovery_is_owned_before_foreman_execution(self):
        import json
        role = source("20_ROLES/ARCHITECT_DISCOVERY.md")
        reconnaissance = source("docs/ARCHITECT_RECONNAISSANCE.md")
        foreman = source("20_ROLES/FOREMAN.md")
        interface = source("docs/AGENT_INTERFACE.md")
        self.assertIn("not a new organizational role", role)
        self.assertIn("single canonical owner of ARCH-0", role)
        self.assertIn("唯一 ARCH-0 规范 owner", reconnaissance)
        self.assertIn("Architect Challenge", role)
        self.assertIn("Architecture Discovery", foreman)
        self.assertIn("architecture_decision", source("50_TEMPLATES/DISPATCH_PAIR.md"))
        self.assertIn("ordinary bugfix", role)
        self.assertIn("新 delegated Work", interface)

        diagram = json.loads(source("docs/diagrams/project.architecture.json"))
        view = next(x for x in diagram["meta"]["views"] if x["id"] == "executionPath")
        self.assertIn("roles", view["focus"])
        role_node = next(x for x in diagram["components"] if x["id"] == "roles")
        pointers = {x["path"] for x in role_node["sources"]}
        self.assertIn("docs/ARCHITECT_RECONNAISSANCE.md", pointers)
        self.assertIn("20_ROLES/FOREMAN.md", pointers)


    def test_foreman_orchestration_first_dynamic_scheduling(self):
        role = source("20_ROLES/FOREMAN.md")
        guidance = source("40_GUIDES/ASYNC_FOREMEN.md")
        self.assertIn("ORCHESTRATION_FIRST", role)
        self.assertIn("不为一个慢 child 阻塞所有独立进展", role)
        self.assertIn("不强制补满并发", role)
        self.assertIn("小范围状态检查", role)
        self.assertIn("child terminal", guidance)
        self.assertIn("关键路径", guidance)
        self.assertIn("不另建具有权威的第二任务数据库", guidance)
        self.assertIn("不自动取消/夺取 Work", guidance)
        self.assertIn("免费模型也不是自动合格的执行者", guidance)
        self.assertIn("Human 为推进工作发出", guidance)


if __name__ == "__main__":
    unittest.main()

import unittest


class Phase3ToolRegistrySchemaTest(unittest.TestCase):
    def _registry(self):
        from ai.runtime.registry import ToolRegistry
        from ai.runtime.results import ToolResult
        from ai.runtime.tools import ToolPermission, ToolSpec

        async def execute(_context, _arguments):
            return ToolResult(
                tool_name="demo",
                call_id="call-1",
                ok=True,
                result_kind="result",
                preview="done",
                payload={},
            )

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="search",
                description="Search indexed content.",
                input_schema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {"query": {"type": "string"}},
                },
                permission=ToolPermission(scope="read"),
                normalize=lambda arguments: arguments,
                execute=execute,
                when_to_use="Use when the planner needs indexed content.",
            )
        )
        registry.register(
            ToolSpec(
                name="write_resource",
                description="Write a resource.",
                input_schema={"type": "object", "properties": {}},
                permission=ToolPermission(scope="write"),
                normalize=lambda arguments: arguments,
                execute=execute,
            )
        )
        return registry

    def test_planner_tool_schemas_only_include_policy_allowed_tools(self):
        from ai.harness.permissions import EffectivePolicy

        schemas = self._registry().planner_tool_schemas(
            EffectivePolicy(
                allowed_tools=["search", "write_resource"],
                denied_tools=["write_resource"],
            )
        )

        self.assertEqual([schema["name"] for schema in schemas], ["search"])
        self.assertEqual(schemas[0]["description"], "Search indexed content.")
        self.assertEqual(
            schemas[0]["when_to_use"],
            "Use when the planner needs indexed content.",
        )
        self.assertEqual(
            schemas[0]["arguments_schema"]["required"],
            ["query"],
        )
        self.assertNotIn("execute", schemas[0])
        self.assertNotIn("normalize", schemas[0])

    def test_validate_tool_arguments_rejects_missing_required_field(self):
        from ai.runtime.schema_validation import ToolSchemaValidationError

        tool = self._registry().get("search")

        with self.assertRaises(ToolSchemaValidationError) as caught:
            tool.validate_arguments({})

        self.assertIn("query is required", str(caught.exception))

    def test_validate_tool_arguments_rejects_wrong_basic_type(self):
        from ai.runtime.schema_validation import ToolSchemaValidationError

        tool = self._registry().get("search")

        with self.assertRaises(ToolSchemaValidationError) as caught:
            tool.validate_arguments({"query": 123})

        self.assertIn("query must be string", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

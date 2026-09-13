import unittest

import core


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.runner = core.ShadowVoidCore()

    def tearDown(self):
        self.runner.end_session()

    def test_all_modules_load_from_slash_paths(self):
        expected = set(core.CONFIG["modules"])
        self.assertEqual(set(core.MODULES), expected)
        self.assertEqual(core.MODULE_LOAD_ERRORS, {})

    def test_command_parser_preserves_quoted_arguments(self):
        result = self.runner.execute_command('scan "target with spaces"')
        self.assertEqual(result["status"], "blocked")

    def test_invalid_dga_count_is_reported(self):
        result = self.runner.execute_command("c2 generate not-a-number")
        self.assertEqual(result["status"], "error")

    def test_dga_is_deterministic_and_does_not_mutate_global_rng(self):
        generator = core.DomainGenerator(10, ["example"])
        first = generator.generate_domains(4)
        second = generator.generate_domains(4)
        self.assertEqual(first, second)
        self.assertTrue(all(domain.endswith(".example") for domain in first))

    def test_arbitrary_code_execution_is_disabled(self):
        self.assertFalse(core.execute_in_memory("raise RuntimeError('should not run')"))

    def test_sensitive_commands_are_blocked(self):
        for command in ("scan host", "exploit CVE-1 host", "pivot host", "exfil a b", "inject list"):
            with self.subTest(command=command):
                self.assertEqual(self.runner.execute_command(command)["status"], "blocked")


if __name__ == "__main__":
    unittest.main()

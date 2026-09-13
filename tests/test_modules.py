import unittest

from modules.auth import AuthModule
from modules.net import NetModule
from modules.post_exploit import PostExploitModule
from modules.process_injection import ProcessInjector
from modules.web import WebModule


class SafeModuleTests(unittest.TestCase):
    def test_active_module_operations_are_blocked(self):
        cases = [
            AuthModule().pass_the_hash("hash", "host"),
            NetModule().dns_spoof("eth0", "example.test", "127.0.0.1"),
            PostExploitModule().exfiltrate("secret", "example.test"),
            WebModule().deploy_webshell("example.test", "/shell.php"),
            ProcessInjector().migrate_to_process("python"),
        ]
        self.assertTrue(all(result["status"] == "blocked" for result in cases))

    def test_process_inventory_is_read_only(self):
        processes = ProcessInjector().list_injectable_processes()
        self.assertIsInstance(processes, list)
        self.assertTrue(all(process["injectable"] is False for process in processes))


if __name__ == "__main__":
    unittest.main()

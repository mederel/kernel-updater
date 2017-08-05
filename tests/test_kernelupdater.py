import unittest
import kernelupdater
import os
from tempfile import mkdtemp


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class KernelUpdaterTest(unittest.TestCase):
    def setUp(self):
        self.temp_root_dir = mkdtemp();

        self.kernel_root_dir = self.temp_root_dir + "/kernels"
        self.modules_root_dir = self.temp_root_dir + "/modules"
        self.grub_root_dir = self.temp_root_dir + "/grub"

        os.mkdir(self.kernel_root_dir)
        os.mkdir(self.modules_root_dir)
        os.mkdir(self.grub_root_dir)

        os.mkdir(self.kernel_root_dir + "/linux-4.11.8-gentoo")
        os.mkdir(self.kernel_root_dir + "/linux-4.12.2-gentoo")
        os.mkdir(self.kernel_root_dir + "/linux-4.12.3-gentoo")
        os.mkdir(self.kernel_root_dir + "/linux-4.12.4-gentoo")
        os.symlink(self.kernel_root_dir + "/linux-4.12.4-gentoo",
                   self.kernel_root_dir + "/linux")

        os.mkdir(self.modules_root_dir + "/4.11.8-gentoo")

        touch(self.grub_root_dir + "/config-4.11.8-gentoo")
        touch(self.grub_root_dir + "/System.map-4.11.8-gentoo")
        touch(self.grub_root_dir + "/vmlinuz-4.11.8-gentoo")
        touch(self.grub_root_dir + "/config-4.11.8-gentoo.old")
        touch(self.grub_root_dir + "/initramfs-genkernel-x86_64-4.11.8-gentoo")
        touch(self.grub_root_dir + "/System.map-4.11.8-gentoo.old")
        touch(self.grub_root_dir + "/vmlinuz-4.11.8-gentoo.old")

        self.command_runner = CommandInterceptor()
        self.selected_kernel = kernelupdater.SelectedKernel(kernel_root_dir=self.kernel_root_dir)

    def test_something(self):
        config_file = self.kernel_root_dir + "/linux-4.12.3-gentoo/.config"
        touch(config_file)

        kernel_updater = kernelupdater.KernelUpdater(config_file=config_file,
                                                     a_selected_kernel=self.selected_kernel,
                                                     a_command_runner=self.command_runner,
                                                     kernel_root_dir=self.kernel_root_dir,
                                                     modules_root_dir=self.modules_root_dir,
                                                     grub_root_dir=self.grub_root_dir)
        kernel_updater.update_kernel()

        for command in self.command_runner.commands:
            if command.startswith("make"):
                self.assertIn("linux-4.12.4-gentoo", command)
            elif command.startswith("genkernel"):
                self.assertEqual("genkernel initramfs", command)
            elif command.startswith("emerge") and "-C" not in command:
                self.assertIn("module-rebuild", command)
            elif command.startswith("emerge"):
                self.assertTrue("4.11.8" in command or "4.12.2" in command)
            elif command.startswith("grub-mkconfig"):
                self.assertIn("grub/grub.cfg", command)
            else:
                self.fail("unexpected command: " + command)

        self.assertNotIn("4.11.8", "".join(os.listdir(self.grub_root_dir)))
        kernel_dirs = "".join(os.listdir(self.kernel_root_dir))
        self.assertNotIn("4.11.8", kernel_dirs)
        self.assertNotIn("4.12.2", kernel_dirs)
        self.assertNotIn("4.11.8", "".join(os.listdir(self.modules_root_dir)))


class CommandInterceptor(kernelupdater.CommandRunner):
    def __init__(self):
        self.commands = []

    def run_command(self, command_array, comment=""):
        self.commands.append(" ".join(command_array))


if __name__ == '__main__':
    unittest.main()

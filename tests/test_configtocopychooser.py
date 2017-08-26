import unittest
import kernelupdater
import os
from tempfile import mkdtemp


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class ConfigToCopyChooserTest(unittest.TestCase):
    def setUp(self):
        self.temp_root_dir = mkdtemp()

        os.mkdir(self.temp_root_dir + "/linux-4.11.8-gentoo")
        os.mkdir(self.temp_root_dir + "/linux-4.12.2-gentoo")
        os.mkdir(self.temp_root_dir + "/linux-4.12.3-gentoo")
        os.mkdir(self.temp_root_dir + "/linux-4.12.4-gentoo")
        os.symlink(self.temp_root_dir + "/linux-4.12.4-gentoo",
                   self.temp_root_dir + "/linux")

        touch(self.temp_root_dir + "/linux-4.11.8-gentoo/.config")
        touch(self.temp_root_dir + "/linux-4.12.2-gentoo/.config")
        touch(self.temp_root_dir + "/linux-4.12.3-gentoo/.config")

        self.selected_kernel = kernelupdater.SelectedKernel(kernel_root_dir=self.temp_root_dir)

    def test_config_in_reverse_order(self):
        config_to_copy_chooser = ConfigToCopyChooserMock(choice=0, selected_kernel=self.selected_kernel, kernel_root_dir=self.temp_root_dir)

        chosen = config_to_copy_chooser.choose_config_file()

        self.assertEqual(self.temp_root_dir + "/linux-4.12.3-gentoo/.config", chosen)


class ConfigToCopyChooserMock(kernelupdater.ConfigToCopyChooser):
    def __init__(self, choice, selected_kernel, kernel_root_dir):
        kernelupdater.ConfigToCopyChooser.__init__(self, selected_kernel=selected_kernel, kernel_root_dir=kernel_root_dir)
        self.choice = str(choice)

    def do_input(self, string_to_display):
        return self.choice


if __name__ == '__main__':
    unittest.main()

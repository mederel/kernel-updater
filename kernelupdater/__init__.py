import os
import shutil
import multiprocessing
from subprocess import call
from operator import itemgetter
from re import sub


KERNEL_ROOT_DIR = "/usr/src"
MODULES_ROOT_DIR = "/lib/modules"
GRUB_ROOT_DIR = "/boot"


class SelectedKernel(object):
    """
    Represents the selected kernel, that is the one /usr/src/linux symbolic link points to
    """

    def __init__(self, kernel_root_dir=KERNEL_ROOT_DIR):
        self.link_folder = kernel_root_dir + "/linux"
        if not os.path.exists(self.link_folder):
            exit(1)  # Error no symlink available for kernel - aborting

        self.selected_kernel = os.readlink(self.link_folder)
        if self.selected_kernel.startswith('/'):
            self.selected_kernel_dir = self.selected_kernel
            self.selected_kernel = self.selected_kernel[self.selected_kernel.rfind('/')+1:]
        else:
            self.selected_kernel_dir = kernel_root_dir + '/' + self.selected_kernel
        print("Selected kernel is: " + self.selected_kernel + " in dir " + self.selected_kernel_dir)


class KernelUpdater(object):
    """
    The class doing the job of updating the kernel, calling the different necessary steps.

    For gentoo only.
    """

    def __init__(self, config_file, a_selected_kernel, a_command_runner, kernel_root_dir=KERNEL_ROOT_DIR,
                 modules_root_dir=MODULES_ROOT_DIR, grub_root_dir=GRUB_ROOT_DIR):
        self.config_file = config_file
        self.selected_kernel = a_selected_kernel
        self.command_runner = a_command_runner
        self.kernel_root_dir = kernel_root_dir
        self.modules_root_dir = modules_root_dir
        self.grub_root_dir = grub_root_dir

    def update_kernel(self):
        self.copy_config_file()
        self.build_kernel()
        self.install_kernel()
        self.generate_initramfs()
        self.rebuild_drivers()

        old_kernel_versions_to_clean = self.get_old_kernels_to_clean()
        self.clean_old_kernels(old_kernel_versions_to_clean)

        self.update_grub()

        print("You can safely reboot now! Thanks for using kernel-updater.py")

    def copy_config_file(self):
        print("Copying " + self.config_file + " to " + self.selected_kernel.link_folder + "/.config")
        shutil.copyfile(self.config_file, self.selected_kernel.link_folder + "/.config")

    def build_kernel(self):
        nb_cpus = multiprocessing.cpu_count()
        build_command = ["make", "-j" + str(nb_cpus + 1), "-C", self.selected_kernel.selected_kernel_dir]
        self.command_runner.run_command(build_command)

    def install_kernel(self):
        install_command = ["make", "-C", self.selected_kernel.selected_kernel_dir, "install"]
        self.command_runner.run_command(install_command)
        self.command_runner.run_command(install_command, "to get .old files created")

        modules_install_command = ["make", "-C", self.selected_kernel.selected_kernel_dir, "modules_install"]
        self.command_runner.run_command(modules_install_command)

    def generate_initramfs(self):
        initramfs_generation_command = ["genkernel", "initramfs"]
        self.command_runner.run_command(initramfs_generation_command)

    def rebuild_drivers(self):
        merge_back_modules_command = ["emerge", "-1q", "@x11-module-rebuild", "@module-rebuild"]
        self.command_runner.run_command(merge_back_modules_command)

    def get_old_kernels_to_clean(self):
        versions = []
        dir_list = os.listdir(self.kernel_root_dir)
        for kernel_dir in dir_list:
            if "linux-" in kernel_dir:
                versions.append(self.get_version_int_array_from_kernel_folder(kernel_dir))
        selected_version = self.get_version_int_array_from_kernel_folder(self.selected_kernel.selected_kernel)
        versions = sorted(versions, key=itemgetter(0, 1, 2, 3))
        index_selected = versions.index(selected_version)
        return [versions[i] for i in range(0, index_selected - 1)]

    def clean_old_kernels(self, old_kernel_versions_to_clean):
        for version in old_kernel_versions_to_clean:
            kernel_version_suffix = self.get_kernel_folder_suffix_from_version_int_array(version)
            version_str = self.get_version_string_from_version_int_array(version)
            print("cleaning up version " + version_str + "...")
            self.command_runner.run_command(["emerge", "-C", "=gentoo-sources-" + version_str])
            self.remove_tree(self.modules_root_dir + "/" + kernel_version_suffix)
            self.remove_tree(self.kernel_root_dir + "/linux-" + kernel_version_suffix)
            boot_versioned_files = os.listdir(self.grub_root_dir)
            for boot_versioned_file in boot_versioned_files:
                if kernel_version_suffix in boot_versioned_file:
                    boot_versioned_path = self.grub_root_dir + "/" + boot_versioned_file
                    print("Removing " + boot_versioned_path)
                    os.remove(boot_versioned_path)

    def update_grub(self):
        grub_mkconfig_command = ["grub-mkconfig", "-o", self.grub_root_dir + "/grub/grub.cfg"]
        self.command_runner.run_command(grub_mkconfig_command)

    @staticmethod
    def get_version_int_array_from_kernel_folder(folder_name):
        string_array = sub('.*linux-', '', folder_name).replace("-gentoo", "").replace("-r", ".").split(".")
        int_array = [int(num_string) for num_string in string_array]
        if len(int_array) == 3:
            int_array.append(-1)
        return int_array

    @staticmethod
    def get_kernel_folder_suffix_from_version_int_array(version_int_array):
        version_string = ".".join(str(version_int_array[index]) for index in [0, 1, 2]);
        revision_suffix = "";
        if version_int_array[3] != -1:
            revision_suffix = "-r" + str(version_int_array[3])
        return version_string + "-gentoo" + revision_suffix

    @staticmethod
    def get_version_string_from_version_int_array(version_int_array):
        version_string = ".".join(str(version_int_array[index]) for index in [0, 1, 2]);
        if version_int_array[3] != int(-1):
            version_string += "-r" + str(version_int_array[3])
        return version_string

    @staticmethod
    def remove_tree(dir_to_delete):
        print("Deleting " + dir_to_delete + "...")
        shutil.rmtree(dir_to_delete, ignore_errors=True)




class CommandRunner(object):
    """
    Runs command line commands. Externalised for tests.
    """

    def run_command(self, command_array, comment=""):
        print("Running " + " ".join(command_array) + (" (" + comment + ")" if comment != "" else ""))
        call(command_array)


class ConfigToCopyChooser(object):
    """
    After the install of a new set of kernel sources, one has to choose which .config file will be used as a starting
    point for the configuration.
    """

    def __init__(self, selected_kernel, kernel_root_dir=KERNEL_ROOT_DIR):
        self.selected_kernel = selected_kernel
        self.kernel_root_dir = kernel_root_dir

    def choose_config_file(self):
        config_files = self.find_config_files()
        config_files.sort(reverse=True)

        print("Select kernel to copy .config from:")
        for idx, config_file_path in enumerate(config_files):
            print("" + str(idx) + " - " + config_file_path)
        chosen_index = int(self.do_input("Choice? [0-" + str(len(config_files) - 1) + "]:"))
        return config_files[chosen_index]

    def find_config_files(self):
        config_files = []
        dir_list = os.listdir(self.kernel_root_dir)
        for kernel_dir in dir_list:
            a_config_file = self.kernel_root_dir + "/" + kernel_dir + "/.config"
            if kernel_dir.startswith("linux-") and os.path.exists(a_config_file) \
                    and kernel_dir != self.selected_kernel.selected_kernel:
                config_files.append(a_config_file)
        return config_files

    def do_input(self, string_to_display):
        return input(string_to_display)


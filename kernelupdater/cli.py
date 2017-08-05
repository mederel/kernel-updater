import argparse
import os

from kernelupdater import SelectedKernel, CommandRunner, KernelUpdater, KERNEL_ROOT_DIR, ConfigToCopyChooser


def main():
    parser = argparse.ArgumentParser(description="Gentoo: builds latest merged kernel, installs it, and does all"
                                                 " necessary post processes")
    parser.add_argument("-f", "--force", help="Force rebuild, reinstall and post processes", action="store_true")
    args = parser.parse_args()

    selected_kernel = SelectedKernel()

    if os.path.exists(KERNEL_ROOT_DIR + "/linux/.config") and not args.force:
        print("A config file exists already in " + KERNEL_ROOT_DIR + "/linux - skipping")
        exit(1)

    command_runner = CommandRunner()
    config_to_copy_chooser = ConfigToCopyChooser(selected_kernel=selected_kernel)

    chosen_config = config_to_copy_chooser.choose_config_file()

    kernel_updater = KernelUpdater(config_file=chosen_config, a_selected_kernel=selected_kernel,
                                   a_command_runner=command_runner)
    kernel_updater.update_kernel()

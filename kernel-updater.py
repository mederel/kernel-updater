#!/usr/bin/env python

import os
import argparse
from shutil import copyfile
import multiprocessing
from subprocess import call

parser = argparse.ArgumentParser(description="Gentoo: builds latest merged kernel, installs it, and does all"
                                             " necessary post processes")
parser.add_argument("-f", "--force", help="Force rebuild, reinstall and post processes", action="store_true")

args = parser.parse_args()


def run_command(command_array, comment=""):
    print("Running " + " ".join(command_array) + (" (" + comment + ")" if comment != "" else ""))
    call(command_array)


linkFolder = "/usr/src/linux"
if not os.path.exists(linkFolder):
    exit(1)  # Error no symlink available for kernel - aborting

selectedKernel = os.readlink(linkFolder)
selectedKernelDir = "/usr/src/" + selectedKernel
print("Selected kernel is: " + selectedKernel + " in dir " + selectedKernelDir)

if os.path.exists("/usr/src/linux/.config") and not args.force:
    print("A config file exists already in /usr/src/linux - skipping")
else:
    configFiles = []
    kernelRootDir = "/usr/src"
    dirList = os.listdir(kernelRootDir)
    for directory in dirList:
        configFile = kernelRootDir + "/" + directory + "/.config"
        if directory.startswith("linux-") and os.path.exists(configFile) \
                and directory != selectedKernel:
            configFiles.append(configFile)

    print("Select kernel to copy .config from:")
    for idx, configFilePath in enumerate(configFiles):
        print("" + str(idx) + " - " + configFilePath)
    s = int(input("Choice? [0-" + str(len(configFiles) - 1) + "]:"))

    print("Copying " + configFiles[s] + " to " + linkFolder + "/.config")
    # copyfile(configFiles[s], linkFolder + "/.config")

    nbCpus = multiprocessing.cpu_count()
    buildCommand = ["make", "-j" + str(nbCpus + 1), "-C", selectedKernelDir]
    # run_command(buildCommand)

    installCommand = ["make", "-C", selectedKernelDir, "install"]
    # run_command(installCommand)
    # run_command(installCommand, "to get .old files created")

    modulesInstallCommand = ["make", "-C", selectedKernelDir, "modules_install"]
    # run_command(modulesInstallCommand)

    initramfsGenerationCommand = ["genkernel", "initramfs"]
    # run_command(initramfsGenerationCommand)

    mergeBackModulesCommand = ["emerge", "-1q", "@x11-module-rebuild", "@module-rebuild"]
    run_command(mergeBackModulesCommand)

    print("You can safely reboot now! Thanks for using kernel-updater.py")

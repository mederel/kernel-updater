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

    def test_prev_v118_v122_v123_new_v124(self):
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

    def test_prev_v1316_v148r1_new_v1410(self):
        os.mkdir(self.kernel_root_dir + "/linux-4.13.16-gentoo")
        touch(self.kernel_root_dir + "/linux-4.13.16-gentoo/.config")
        os.mkdir(self.kernel_root_dir + "/linux-4.14.8-gentoo-r1")
        config_file = self.kernel_root_dir + "/linux-4.14.8-gentoo-r1/.config"
        touch(config_file)
        os.mkdir(self.kernel_root_dir + "/linux-4.14.10-gentoo")
        os.symlink(self.kernel_root_dir + "/linux-4.14.10-gentoo",
                   self.kernel_root_dir + "/linux")

        os.mkdir(self.modules_root_dir + "/4.13.16-gentoo")
        os.mkdir(self.modules_root_dir + "/4.14.8-gentoo-r1")

        touch(self.grub_root_dir + "/config-4.13.16-gentoo")
        touch(self.grub_root_dir + "/System.map-4.13.16-gentoo")
        touch(self.grub_root_dir + "/initramfs-genkernel-x86_64-4.13.16-gentoo")
        touch(self.grub_root_dir + "/vmlinuz-4.13.16-gentoo")
        touch(self.grub_root_dir + "/config-4.13.16-gentoo.old")
        touch(self.grub_root_dir + "/System.map-4.13.16-gentoo.old")
        touch(self.grub_root_dir + "/vmlinuz-4.13.16-gentoo.old")

        touch(self.grub_root_dir + "/config-4.14.8-gentoo-r1")
        touch(self.grub_root_dir + "/System.map-4.14.8-gentoo-r1")
        touch(self.grub_root_dir + "/initramfs-genkernel-x86_64-4.14.8-gentoo-r1")
        touch(self.grub_root_dir + "/vmlinuz-4.14.8-gentoo-r1")
        touch(self.grub_root_dir + "/config-4.14.8-gentoo-r1.old")
        touch(self.grub_root_dir + "/System.map-4.14.8-gentoo-r1.old")
        touch(self.grub_root_dir + "/vmlinuz-4.14.8-gentoo-r1.old")

        self.command_runner = CommandInterceptor()
        self.selected_kernel = kernelupdater.SelectedKernel(kernel_root_dir=self.kernel_root_dir)

        kernel_updater = kernelupdater.KernelUpdater(config_file=config_file,
                                                     a_selected_kernel=self.selected_kernel,
                                                     a_command_runner=self.command_runner,
                                                     kernel_root_dir=self.kernel_root_dir,
                                                     modules_root_dir=self.modules_root_dir,
                                                     grub_root_dir=self.grub_root_dir)
        kernel_updater.update_kernel()

        for command in self.command_runner.commands:
            if command.startswith("make"):
                self.assertIn("linux-4.14.10-gentoo", command)
            elif command.startswith("genkernel"):
                self.assertEqual("genkernel initramfs", command)
            elif command.startswith("emerge") and "-C" not in command:
                self.assertIn("module-rebuild", command)
            elif command.startswith("emerge"):
                self.assertTrue("4.13.16" in command or "4.14.8" in command)
            elif command.startswith("grub-mkconfig"):
                self.assertIn("grub/grub.cfg", command)
            else:
                self.fail("unexpected command: " + command)

        self.assertNotIn("4.13.16", "".join(os.listdir(self.grub_root_dir)))
        self.assertNotIn("4.13.16", "".join(os.listdir(self.kernel_root_dir)))
        self.assertNotIn("4.13.16", "".join(os.listdir(self.modules_root_dir)))

# INSTALL net/netfilter/xt_LOG.ko
#   INSTALL net/netfilter/xt_addrtype.ko
#   INSTALL net/netfilter/xt_mark.ko
#   INSTALL net/netfilter/xt_nat.ko
#   DEPMOD  4.14.10-gentoo
# make: Leaving directory '/usr/src/linux-4.14.10-gentoo'
# Running genkernel initramfs
# * Gentoo Linux Genkernel; Version 66
# * Running with options: initramfs
#
# * Using genkernel.conf from /etc/genkernel.conf
# * Sourcing arch-specific config.sh from /usr/share/genkernel/arch/x86_64/config.sh ..
# * Sourcing arch-specific modules_load from /usr/share/genkernel/arch/x86_64/modules_load ..
#
# * Linux Kernel 4.14.10-gentoo for x86_64...
# * .. with config file /usr/share/genkernel/arch/x86_64/kernel-config
# * busybox: >> Using cache
# * initramfs: >> Initializing...
# *         >> Appending base_layout cpio data...
# *         >> Appending udev cpio data...
# cp: cannot stat '/etc/modprobe.d/blacklist.conf': No such file or directory
# * cannot copy /etc/modprobe.d/blacklist.conf from udev
# *         >> Appending auxilary cpio data...
# *         >> Copying keymaps
# *         >> Appending busybox cpio data...
# *         >> Appending modules cpio data...
# *         >> Appending blkid cpio data...
# *         >> Skipping modprobed copy
# *         >> Appending ld_so_conf cpio data...
# * ldconfig: adding /sbin/ldconfig...
# * ld.so.conf: adding /etc/ld.so.conf{.d/*,}...
# cpio: lib64 not created: newer or same age version exists
# cpio: lib64 not created: newer or same age version exists
# cpio: lib64/libblkid.so.1 not created: newer or same age version exists
# cpio: lib64/libc.so.6 not created: newer or same age version exists
# cpio: lib64/ld-linux-x86-64.so.2 not created: newer or same age version exists
# cpio: lib64/libuuid.so.1 not created: newer or same age version exists
# *         >> Finalizing cpio...
# *         >> Compressing cpio data (.xz)...
#
# * WARNING... WARNING... WARNING...
# * Additional kernel cmdline arguments that *may* be required to boot properly...
# * With support for several ext* filesystems available, it may be needed to
# * add "rootfstype=ext3" or "rootfstype=ext4" to the list of boot parameters.
#
# * Do NOT report kernel bugs as genkernel bugs unless your bug
# * is about the default genkernel configuration...
# *
# * Make sure you have the latest ~arch genkernel before reporting bugs.
# Running emerge -1q @x11-module-rebuild @module-rebuild
# >>> Verifying ebuild manifests
# >>> Running pre-merge checks for x11-base/xorg-server-1.19.6
# >>> Running pre-merge checks for x11-drivers/xf86-input-synaptics-1.9.0
#  * Determining the location of the kernel source code
#  * Found kernel source directory:
#  *     /usr/src/linux
#  * Found kernel object directory:
#  *     /lib/modules/4.14.10-gentoo/build
#  * Found sources for kernel version:
#  *     4.14.10-gentoo
# >>> Running pre-merge checks for x11-drivers/xf86-input-evdev-2.10.5
#  * Determining the location of the kernel source code
#  * Found kernel source directory:
#  *     /usr/src/linux
#  * Found kernel object directory:
#  *     /lib/modules/4.14.10-gentoo/build
#  * Found sources for kernel version:
#  *     4.14.10-gentoo
#  * Checking for suitable kernel configuration options...                                                                                                   [ ok ]
# >>> Running pre-merge checks for x11-drivers/nvidia-drivers-387.34
#  * Determining the location of the kernel source code
#  * Found kernel source directory:
#  *     /usr/src/linux
#  * Found kernel object directory:
#  *     /lib/modules/4.14.10-gentoo/build
#  * Found sources for kernel version:
#  *     4.14.10-gentoo
#  * Checking for suitable kernel configuration options...                                                                                                   [ ok ]
# >>> Emerging (1 of 8) x11-base/xorg-server-1.19.6::gentoo
# >>> Installing (1 of 8) x11-base/xorg-server-1.19.6::gentoo
# >>> Emerging (2 of 8) sys-block/rts5229-1.07-r6::gentoo
# >>> Installing (2 of 8) sys-block/rts5229-1.07-r6::gentoo
# >>> Emerging (3 of 8) sys-block/rts_pstor-1.10-r5::gentoo
# >>> Installing (3 of 8) sys-block/rts_pstor-1.10-r5::gentoo
# >>> Emerging (4 of 8) x11-drivers/xf86-input-keyboard-1.9.0::gentoo
# >>> Installing (4 of 8) x11-drivers/xf86-input-keyboard-1.9.0::gentoo
# >>> Emerging (5 of 8) x11-drivers/xf86-input-synaptics-1.9.0::gentoo
# >>> Installing (5 of 8) x11-drivers/xf86-input-synaptics-1.9.0::gentoo
# >>> Emerging (6 of 8) x11-drivers/xf86-input-evdev-2.10.5::gentoo
# >>> Installing (6 of 8) x11-drivers/xf86-input-evdev-2.10.5::gentoo
# >>> Emerging (7 of 8) x11-drivers/xf86-input-mouse-1.9.2::gentoo
# >>> Installing (7 of 8) x11-drivers/xf86-input-mouse-1.9.2::gentoo
# >>> Emerging (8 of 8) x11-drivers/nvidia-drivers-387.34::gentoo
# >>> Installing (8 of 8) x11-drivers/nvidia-drivers-387.34::gentoo
# Running grub-mkconfig -o /boot/grub/grub.cfg
# Generating grub configuration file ...
# Found linux image: /boot/vmlinuz-4.14.10-gentoo
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.14.10-gentoo
# Found linux image: /boot/vmlinuz-4.14.10-gentoo.old
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.14.10-gentoo
# Found linux image: /boot/vmlinuz-4.14.8-gentoo-r1
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.14.8-gentoo-r1
# Found linux image: /boot/vmlinuz-4.14.8-gentoo-r1.old
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.14.8-gentoo-r1
# Found linux image: /boot/vmlinuz-4.13.16-gentoo
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.13.16-gentoo
# Found linux image: /boot/vmlinuz-4.13.16-gentoo.old
# Found initrd image: /boot/initramfs-genkernel-x86_64-4.13.16-gentoo
#   /run/lvm/lvmetad.socket: connect failed: No such file or directory
#   WARNING: Failed to connect to lvmetad. Falling back to internal scanning.
# Found Windows 8 (loader) on /dev/sda1
# done
# You can safely reboot now! Thanks for using kernel-updater.py


class CommandInterceptor(kernelupdater.CommandRunner):
    def __init__(self):
        self.commands = []

    def run_command(self, command_array, comment=""):
        self.commands.append(" ".join(command_array))


if __name__ == '__main__':
    unittest.main()

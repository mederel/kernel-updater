Gentoo kernel updater
=====================

This python script is to be used after each install of a newer version of your sys-kernel/gentoo-sources under Gentoo. It will do the following for you:

* copy the ``.config`` file from another already kernel version of your choosing
* build the kernel
* install it
* install the built modules
* generate a initramfs with ``genkernel``
* rebuild all modules with ``emerge`` and the set ``@module-rebuild``
* remove versions older than 1 version before the current
* update grub configuration with ``grub-mkconfig``

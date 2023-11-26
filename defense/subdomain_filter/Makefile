# Copied and adapted from https://stackoverflow.com/questions/29553990/print-tcp-packet-data

ifeq ($(KERNELRELEASE),)
	
KERNELDIR ?= /lib/modules/$(shell uname -r)/build

module:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) C=1 modules

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) C=1 clean

.PHONY: module clean

else

MODULE = subdomain_filter.o
CFLAGS_$(MODULE) := -DDEBUG
obj-m := $(MODULE)

endif


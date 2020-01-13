IPXE_IMG=ipxe/src/bin/ipxe.iso

all: ipxe-boot.img ipxe-boot.qcow2

ipxe-boot.img: $(IPXE_IMG) script.ipxe
	cp $(IPXE_IMG) $@

ipxe-boot.qcow2: ipxe-boot.img
	qemu-img convert -f raw -O qcow2 $< $@

# We disable -Werror so we can build older commits with newer gcc
$(IPXE_IMG):
	$(MAKE) -C ipxe/src NO_WERROR=1 EMBED=../../script.ipxe bin/ipxe.iso

clean:
	$(MAKE) -C ipxe/src clean
	rm -f ipxe-boot.img ipxe-boot.qcow2

.PHONY: $(IPXE_IMG) clean all

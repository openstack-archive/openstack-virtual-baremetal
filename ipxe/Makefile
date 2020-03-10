# The location of the directory containing the iPXE make file
# Override this to build from a different source directory
IPXE_SRCDIR=ipxe/src

# The specific image to use as the OVB iPXE boot image
# Override this to use a different image (e.g. ipxe.hd)
IPXE_IMG=ipxe.iso

ipxe_img_path=$(IPXE_SRCDIR)/bin/$(IPXE_IMG)

all: ipxe-boot.img ipxe-boot.qcow2

ipxe-boot.img: $(ipxe_img_path) script.ipxe
	cp $< $@

ipxe-boot.qcow2: ipxe-boot.img
	qemu-img convert -f raw -O qcow2 $< $@

# iPXE is configured by setting config macros in the source tree. The repo
# contains a number of config headers in ipxe/src/config/*.h which contain
# defaults. These defaults can be overridden by creating a corresponding header
# in ipxe/src/config/local.
# For example, the source repo contains ipxe/src/config/general.h, which
# explicitly does not define NET_PROTO_IPV6. To enable IPv6 support in iPXE we
# need to create ipxe/src/config/local/general.h and define NET_PROTO_IPV6 in
# that header.
# The following allows OVB to keep iPXE configuration under ipxe-config in this
# repo, and copies it into place in the iPXE repo during build.

# config_headers is a list of the filenames of all overridden headers in ipxe-config/
config_headers = $(foreach header,$(wildcard ipxe-config/*.h),\
		           $(patsubst ipxe-config/%,%,$(header)))

# repo_config_path is the path to local override headers in the ipxe repo
repo_config_path = $(IPXE_SRCDIR)/config/local

# repo_config_headers is a list of all overridden headers in the iPXE repo
repo_config_headers = $(foreach header,$(config_headers),$(repo_config_path)/$(header))

# Copy individual repo_config_headers from ipxe-config/
$(repo_config_path): ; mkdir $@
$(repo_config_path)/%.h: ipxe-config/%.h | $(repo_config_path)
	cp $< $@

# We disable -Werror so we can build older commits with newer gcc
# Don't use parallel make, as this races to initialise config headers in a
# clean repo.
$(ipxe_img_path): $(repo_config_headers)
	$(MAKE) -C ipxe/src NO_WERROR=1 EMBED=../../script.ipxe bin/$(IPXE_IMG)

clean:
	$(MAKE) -C ipxe/src clean
	rm -f ipxe-boot.img ipxe-boot.qcow2

.PHONY: $(ipxe_img_path) clean

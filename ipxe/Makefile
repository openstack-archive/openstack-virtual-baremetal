# git ref to checkout from the iPXE git repository
# This is the current SHA for HEAD on 9 Aug 2019

IPXE_GIT_REF=c63ef427

ipxe-boot.qcow2:
	ELEMENTS_PATH=./elements IPXE_GIT_REF=$(IPXE_GIT_REF) disk-image-create -x -o ipxe-boot ipxe-boot-image

clean:
	rm -f ipxe-boot.qcow2

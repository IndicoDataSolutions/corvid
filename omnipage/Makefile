OCRLIBPATH = /usr/local/lib/nuance-omnipage-csdk-lib64-20.2
OCRINCPATH = /usr/local/include/nuance-omnipage-csdk-20.2

CXXFLAGS = -O3

.PHONY: auto

auto: corvid
	@echo "Building PDF parser for Tables for corvid app"

corvid: corvid.cpp
	g++ $(CXXFLAGS) -I $(OCRINCPATH) corvid.cpp -o $@ -L $(OCRLIBPATH) -lrecapiplus -lkernelapi -lrecpdf -Wl,-rpath-link,$(OCRLIBPATH),-rpath,$(OCRLIBPATH)


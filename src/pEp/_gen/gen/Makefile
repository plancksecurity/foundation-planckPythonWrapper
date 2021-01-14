include ../Makefile.conf

YML2_FILE=py_module.yml2
YSL2_FILE=$(shell pEp_acid_gen-config)
PYBIND11_FILE=py_module.pybind11

$(info -----SYNTH_SHED GEN----)
$(info YML2_FILE 	$(YML2_FILE))
$(info YSL2_FILE 	$(YSL2_FILE))
$(info CC_FILE 		$(PYBIND11_FILE))

.PHONY = yml pybind11

all: $(PYBIND11_FILE)

$(YML2_FILE): config.json
	pEp_acid_gen $^

$(PYBIND11_FILE) : $(YML2_FILE)
	yml2proc --encoding=utf8 -y $(YSL2_FILE) $(YML2_FILE)

clean:
	rm -f $(YML2_FILE)
	rm -f $(PYBIND11_FILE)


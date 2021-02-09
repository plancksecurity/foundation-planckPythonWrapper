include ../Makefile.conf

YML2_FILE=py_module.yml2
YSL2_FILE=$(shell pEp_acid_gen-config)
PYBIND11_FILE=py_module.pybind11
DEBUG_AST_FILE=adapter_main.hh.ast.json
DEBUG_ACID_FILE=adapter_main.hh.acid.json
DEBUG_YML_FILE=adapter_main.hh.acid.yml

$(info -----_gen GEN----)
$(info YML2_FILE 	$(YML2_FILE))
$(info YSL2_FILE 	$(YSL2_FILE))
$(info CC_FILE 		$(PYBIND11_FILE))

.PHONY = all yml pybind

all: pybind

yml: $(YML2_FILE)

pybind: $(YML2_FILE) $(PYBIND11_FILE)

$(YML2_FILE): config.json
	pEp_acid_gen $^

$(PYBIND11_FILE) : $(YML2_FILE)
	yml2proc --encoding=utf8 -y $(YSL2_FILE) $(YML2_FILE)

clean:
	rm -f $(YML2_FILE)
	rm -f $(PYBIND11_FILE)
	rm -f $(DEBUG_AST_FILE)
	rm -f $(DEBUG_ACID_FILE)
	rm -f $(DEBUG_YML_FILE)


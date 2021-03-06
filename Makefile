# Makefile inspired by Cookiecutter Data Science: https://goo.gl/61Y3zy

.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################


PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = hcm
PYTHON_INTERPRETER = python3
PIP = pip3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install dependencies
reqs: test-env
	$(PIP) install -r requirements.txt --ignore-installed six

## Delete all compiled py files
clean:
	find . -name "*.pyc" -exec rm {} \;

## Install development dependencies
dev-reqs: requirements
	$(PIP) install -r dev_requirements.txt --ignore-installed six

## Lint project
lint:
	$(PYTHON_INTERPRETER) -m flake8 --exclude=lib/,bin/,docs/conf.py --ignore F401,H301,E203,E241 hcm

## Install git pre-push and pre-submit checks
hooks:
	cp .github/hooks/* .git/hooks/.
	chmod +x .git/hooks/pre-push
	chmod +x .git/hooks/pre-commit

## Set up virtual environment
env:
ifeq (True,$(HAS_CONDA))
	@echo ">>> Detected conda, creating conda environment."
	conda create --name $(PROJECT_NAME) python=3.6
	@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m venv $(PROJECT_NAME)
	@echo ">>> New venv created. Activate with:\nsource $(PROJECT_NAME)/bin/activate"
endif

## Test python environment is setup correctly
test-env:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

# TODO(#12)

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')

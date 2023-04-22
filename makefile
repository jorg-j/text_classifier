VENV_NAME := .venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate

.PHONY: all
all: $(VENV_ACTIVATE)
	. $(VENV_ACTIVATE); python main.py

$(VENV_ACTIVATE): requirements.txt
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	. $(VENV_ACTIVATE); pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(VENV_NAME)

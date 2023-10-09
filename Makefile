fmt:
	black scripts
	isort scripts

exportenv:
	conda env export | grep -v "^prefix: " > environment.yml

init_py_env:
	@python3 -m venv .venv

venv_activate:
	@echo "-----Going to venv"
	@source .venv/bin/activate

jupyter_install_env:
	@echo "-----Going to venv"
	# @source .venv/bin/activate  
	@echo "-----Install jupyterlab"
	@pip install jupyterlab
	@echo "-----Install notebook"
	@pip install notebook

jupyter_open_port_colab:
	@jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=8888 --NotebookApp.port_retries=0

dino_run:
	@python ./notebooks/SeleniumHelper.py

FROM quay.io/jupyter/docker-stacks-foundation:python-3.12
RUN pip install pyjwt flask mitmproxy 
RUN pip install pip-audit bogrod
RUN pip install locust presidio
RUN pip install torch garak spacy presidio deepeval ragas --extra-index-url https://download.pytorch.org/whl/cpu
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download de_core_news_sm
RUN pip install ipython
RUN pip install dspy
RUN pip install jupyterlab ipywidgets
ADD scripts scripts

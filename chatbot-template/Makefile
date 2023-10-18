.PHONY: streamlitrun
streamlitrun: ## Run the code locally.
	streamlit run main.py --server.runOnSave true

.PHONY: docker-build
docker-build: 
	docker build -t agent .

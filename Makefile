guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
    fi

run-dev-env:
	bash bin/run_dev_env.sh


apply-lint:
	python -m black .

download-podcast-index-db:
	wget https://public.podcastindex.org/podcastindex_feeds.db.tgz \
		--output-document=podscape/podcast_index_db/data/podcastindex_feeds.db.tgz
	tar -xvzf podscape/podcast_index_db/data/podcastindex_feeds.db.tgz -C podscape/podcast_index_db/data/
	rm podscape/podcast_index_db/data/podcastindex_feeds.db.tgz

run-app:
	streamlit run podscape/podcast_index_db/app.py
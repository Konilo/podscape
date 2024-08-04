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
	wget https://public.podcastindex.org/podcastindex_feeds.db.tgz -O podscape/podcast_index_db/podcastindex_feeds.db.tgz
	tar -xvzf podscape/podcast_index_db/podcastindex_feeds.db.tgz -C podscape/podcast_index_db/
	rm podscape/podcast_index_db/podcastindex_feeds.db.tgz

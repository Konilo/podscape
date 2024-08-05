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
	# Download the DB as a tgz file
	wget https://public.podcastindex.org/podcastindex_feeds.db.tgz \
		--output-document=podscape/podcast_index_db/data/podcastindex_feeds.db.tgz
	# Unzip the DB file
	tar -xvzf podscape/podcast_index_db/data/podcastindex_feeds.db.tgz -C podscape/podcast_index_db/data/
	# Remove the tgz file
	rm podscape/podcast_index_db/data/podcastindex_feeds.db.tgz
	# Create index on the title column of the podcasts table
	sqlite3 podscape/podcast_index_db/data/podcastindex_feeds.db "CREATE INDEX title_index ON podcasts(title);"


run-app:
	streamlit run podscape/podcast_index_db/app.py
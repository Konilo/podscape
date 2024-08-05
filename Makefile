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
	# Downloading the DB as a tgz file
	@wget https://public.podcastindex.org/podcastindex_feeds.db.tgz \
		--output-document=podscape/podcast_index_db/data/podcastindex_feeds.db.tgz
	# Removing the old DB file
	@rm podscape/podcast_index_db/data/podcastindex_feeds.db
	# Unzipping the DB file
	@tar -xvzf podscape/podcast_index_db/data/podcastindex_feeds.db.tgz -C podscape/podcast_index_db/data/
	# Removing the tgz file
	@rm podscape/podcast_index_db/data/podcastindex_feeds.db.tgz
	# Creating index on the title column of the podcasts table (this takes >5 minutes)
	@sqlite3 \
		podscape/podcast_index_db/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX title_index ON podcasts(title);"
	# Creating index on the oldestItemPubdate column of the podcasts table (this takes >5 minutes)
	@sqlite3 \
		podscape/podcast_index_db/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX oldestItemPubdate_index ON podcasts(oldestItemPubdate);"
	# Replace impossible oldestItemPubdate values (<Oct. 2002) with NULL
	# https://en.wikipedia.org/wiki/History_of_podcasting#The_RSS_connection
	@sqlite3 \
		podscape/podcast_index_db/data/podcastindex_feeds.db \
		".progress 1000000" \
		"UPDATE podcasts SET oldestItemPubdate = NULL WHERE oldestItemPubdate < 1033430400"


run-app:
	streamlit run podscape/podcast_index_db/app.py
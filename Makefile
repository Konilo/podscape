guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
    fi

run-dev-env:
	bash bin/run_dev_env.sh

etl-enrich:
	# ETL the data
	## Create data directory if it doesn't exist
	@mkdir -p podscape/data
	## Downloading the DB as a tgz file
	@wget https://public.podcastindex.org/podcastindex_feeds.db.tgz \
		--output-document=podscape/data/podcastindex_feeds.db.tgz
	## Removing the old DB file
	@rm -f scape/data/podcastindex_feeds.db
	## Unzipping the DB file (this takes a few minutes)
	@tar -xvzf podscape/data/podcastindex_feeds.db.tgz -C podscape/data/
	## Removing the tgz file
	@rm podscape/data/podcastindex_feeds.db.tgz
	## Creating index on the title column of the podcasts table (this takes >5 minutes)
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX title_index ON podcasts(title);"
	## Creating index on the oldestItemPubdate column of the podcasts table (this takes >5 minutes)
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX oldestItemPubdate_index ON podcasts(oldestItemPubdate);"
	## Creating index on the host column of the podcasts table (this takes >5 minutes)
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX host_index ON podcasts(host);"
	## Replace impossible oldestItemPubdate values (<Oct. 2002) with NULL
	## https://en.wikipedia.org/wiki/History_of_podcasting#The_RSS_connection
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"UPDATE podcasts SET oldestItemPubdate = NULL WHERE oldestItemPubdate < 1033430400"
	# Enrich the data
	## Create podcasts_per_host_day enriched table
	@sqlite3 \
        podscape/data/podcastindex_feeds.db \
        ".progress 1000000" \
        "CREATE TABLE IF NOT EXISTS podcasts_per_host_day AS \
        SELECT \
            DATE(oldestItemPubdate, 'unixepoch') as date, \
            COALESCE(host, 'unknown') as host, \
            COUNT(*) AS '# podcasts created' \
        FROM podcasts \
        WHERE oldestItemPubdate IS NOT NULL \
        GROUP BY 1, 2"

run-app:
	streamlit run podscape/app.py
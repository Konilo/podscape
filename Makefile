guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
    fi

run-dev-env:
	bash bin/run_dev_env.sh

etl-enrich:
	# ETL
	## Creating data directory if it doesn't exist
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@mkdir -p podscape/data
	## Downloading the DB as a tgz file
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@wget https://public.podcastindex.org/podcastindex_feeds.db.tgz \
		--output-document=podscape/data/podcastindex_feeds.db.tgz
	## Removing the old DB file
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@rm -f scape/data/podcastindex_feeds.db
	## Unzipping the DB file (this takes a few minutes)
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@tar -xvzf podscape/data/podcastindex_feeds.db.tgz -C podscape/data/
	## Removing the tgz file
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@rm podscape/data/podcastindex_feeds.db.tgz
	## Creating index on the title column of the podcasts table (this takes >5 minutes)
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX title_index ON podcasts(title);"
	## Creating index on the oldestItemPubdate column of the podcasts table (this takes >5 minutes)
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX oldestItemPubdate_index ON podcasts(oldestItemPubdate);"
	## Creating index on the host column of the podcasts table (this takes >5 minutes)
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"CREATE INDEX host_index ON podcasts(host);"
	## Replacing impossible oldestItemPubdate values (<Oct. 2002) with NULL
	## https://en.wikipedia.org/wiki/History_of_podcasting#The_RSS_connection
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
	@sqlite3 \
		podscape/data/podcastindex_feeds.db \
		".progress 1000000" \
		"UPDATE podcasts SET oldestItemPubdate = NULL WHERE oldestItemPubdate < 1033430400"
	# Enrichment
	## Creating podcasts_per_host_day enriched table
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"
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
	@echo "$$(date +%Y-%m-%d_%H:%M:%S)"

run-app:
	streamlit run podscape/app.py

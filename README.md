# elasticsearch-urlfetch
Provides a URLFetchConnection `connection_class` for https://github.com/elastic/elasticsearch-py

This allows Elasticsearch instances to directly interface URLFetch, rather than being
patched through `Requests` or `urllib3`.

## Usage:

```python
    from elasticsearch_urlfetch import URLFetchConnection

    es = Elasticsearch(connection_class=URLFetchConnection)
    ...
```

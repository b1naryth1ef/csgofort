DEFAULT_INDEX = {
    "settings": {
        "number_of_shards": 1,
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type":     "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 25
                }
            },
            "analyzer": {
                "autocomplete": {
                    "type":      "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter"
                    ]
                }
            }
        }
    }
}

def create_default_mapping(index, field):
    return {
        index: {
            "properties": {
                field: {
                    "type":     "string",
                    "analyzer": "autocomplete"
                }
            }
        }
    }

ES_INDEXES = {
    "marketitems": DEFAULT_INDEX
}

ES_MAPPINGS = {
    "marketitems": {
        "marketitem": create_default_mapping("marketitem", "name")
    }
}

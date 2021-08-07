def register_search_config_from_dict(config_registry, config_dict):
    from snosearch.configs import SearchConfig
    name = config_dict['name']
    search_config = SearchConfig(name, config_dict)
    config_registry.add(search_config)

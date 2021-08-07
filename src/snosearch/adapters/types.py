class TypeAdapter:

    def __init__(self, **kwargs):
        self.schema = kwargs.pop('schema', None)
        self.subtypes = kwargs.pop('subtypes', [kwargs.get('name')])
        self.item_type = kwargs.pop('item_type', None)
        self.factory = self
        self.type_info = self
        self.__dict__.update(kwargs)


def register_type_from_dict(type_registry, type_dict):
    name = type_dict['name']
    item_type = type_dict.get('item_type')
    type_registry[name] = TypeAdapter(**type_dict)
    if item_type:
        type_registry[item_type] = type_registry[name]

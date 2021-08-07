class TypeAdapter:

    def __init__(self, **kwargs):
        self.schema = kwargs.pop('schema')
        self.subtypes = kwargs.pop('subtypes', ['Item'])
        self.item_type = kwargs.pop('item_type')
        self.factory = self
        self.__dict__.update(kwargs)


def register_type_from_dict(type_registry, type_dict):
    name = type_dict['name']
    type_registry[name] = TypeAdapter(**type_dict)

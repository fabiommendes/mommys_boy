from __future__ import absolute_import
from __future__ import unicode_literals

import warnings

from django.db.models import Model as Model
from factory import Factory
from factory.django import DjangoModelFactory, DjangoOptions
from factory import base
from faker import Factory as FakeFactory

fake = FakeFactory.create()


class MommyOptions(DjangoOptions):
    """
    Define additional options for DjangoMommyFactory subclasses.
    """

    def _build_default_options(self):
        return super()._build_default_options() + [
            base.OptionDefault('auto_fields', None, inherit=True),
            base.OptionDefault('auto_exclude', (), inherit=True),
            base.OptionDefault('recipe', None, inherit=True),
        ]


class MommyMeta(type(DjangoModelFactory)):
    """
    Metaclass for DjangoMommyFactory models.
    """
    _global_models_cache = {}
    _forbidden_fields = ('id',)
    _fake_extra = {
        name.replace('_', ''): getattr(fake, name)
        for name in dir(fake)
        if not name.startswith('_')
        }

    def __init__(self, *args):
        super().__init__(*args)

        self._forbidden_fields += self._get_declared_fields()
        self._forbidden_fields += self._meta.auto_exclude
        if self._meta.recipe == 'global':
            model = self._meta.model
            if model not in self._global_models_cache:
                self._global_models_cache[model] = self
            else:
                warnings.warn(
                    'global DjangoMommyFactory for %s.%s is already '
                    'registered. ignoring it.' % (model.__module__,
                                                  model.__name__),
                    RuntimeWarning,
                    stacklevel=2,
                )

        if self._meta.abstract is False:
            self._faker_fields = self._get_faker_fields()

    def _get_faker_fields(self):
        """
        Return a mapping of name: faker_function for all fields that have a name
        corresponding to a faker function.

        Fields in the ._forbidden_fields list are not included.
        """

        fields = {}
        for field in self._meta.model._meta.fields:
            name = field.name
            if (name in self._forbidden_fields or
                    (self._meta.auto_fields is not None and
                     name not in self._meta.auto_fields)):
                continue

            # Try to find a fake function for the given field
            faker = getattr(fake, name, None)
            if faker is None:
                faker = getattr(fake, name.replace('_', ''), None)
            if faker is None:
                faker = self._fake_extra.get(name, None)
            if faker is None:
                continue

            fields[name] = faker

        return fields

    def _get_declared_fields(self):
        """
        Return a tuple with all explicit field declarations.
        """

        return tuple(self._meta.declarations)


class MommyFactoryBase(object):
    class Meta:
        abstract = True

    _options_class = MommyOptions

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._mommy_build_or_create(True, model_class, *args, **kwargs)

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return cls._mommy_build_or_create(False, model_class, *args, **kwargs)

    @classmethod
    def _mommy_build_or_create(cls, create, model_class, *args, **kwargs):
        from model_mommy import mommy
        kwargs = cls._normalize_args(*args, **kwargs)
        if create:
            return mommy.make(model_class, **kwargs)
        else:
            return mommy.prepare(model_class, **kwargs)

    @classmethod
    def _normalize_args(cls, *args, **kwargs):
        kwargs = dict(cls._faker_fields, **kwargs)
        if args:
            raise NotImplemented('positional arguments are not supported')
        return kwargs

    @classmethod
    def _get_mommy_args(cls, _create, **kwargs):
        return cls._normalize_args(**cls.attributes(_create, kwargs))


class MommyManager(object):
    """
    Implements the global mommy object.
    """

    @property
    def _mommy(self):
        try:
            return self.__mommy
        except AttributeError:
            from model_mommy import mommy
            self.__mommy = mommy
            return mommy

    def __init__(self):
        self._model_cache = {}

    def get_factory(self, model_class):
        """
        Return the DjangoMommyFactory subclass associated with the given model.
        """
        if isinstance(model_class, str):
            model_class = self._mommy.Mommy.finder.get_model(model_class)

        factory = MommyMeta._global_models_cache.get(model_class, None)
        if factory is None:
            factory = self._model_cache.get(model_class, None)
        if factory is None:
            class Factory(DjangoMommyFactory):
                class Meta:
                    model = model_class

            factory = self._model_cache[model_class] = Factory
        return factory

    def _get_mommy_args(self, model, _create, **kwargs):
        if issubclass(model, Model):
            factory = self.get_factory(model)
        elif issubclass(model, DjangoMommyFactory):
            factory = model
        elif issubclass(model, Factory):
            return Factory.attributes(_create, kwargs)
        else:
            raise TypeError('argument must be a model instance or a '
                            'DjangoMommyFactory subclass')
        kwargs = factory._get_mommy_args(_create, **kwargs)
        return kwargs

    def _get_model(self, model):
        if issubclass(model, Model):
            return model
        return model._meta.model

    def make(self, model, _quantity=None, make_m2m=False, **kwargs):
        kwargs = self._get_mommy_args(model, True, **kwargs)
        model = self._get_model(model)
        return self._mommy.make(model, _quantity, make_m2m, **kwargs)

    def prepare(self, model, _quantity=None, **kwargs):
        kwargs = self._get_mommy_args(model, False, **kwargs)
        model = self._get_model(model)
        return self._mommy.prepare(model, _quantity, **kwargs)

    def create(self, *args, **kwargs):
        """
        An alias to mommy.make()
        """

        return self.make(*args, **kwargs)

    def build(self, *args, **kwargs):
        """
        An alias to mommy.prepare()
        """

        return self.prepare(*args, **kwargs)

# Initialize export symbols
DjangoMommyFactory = MommyMeta(
    'DjangoMommyFactory',
    (MommyFactoryBase, DjangoModelFactory), {
        '__doc__': """
        Base class for Mommy-enabled factories.
        """
    }
)
mommy = MommyManager()

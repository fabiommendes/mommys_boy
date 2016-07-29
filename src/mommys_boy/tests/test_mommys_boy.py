import pytest
from django.contrib.auth.models import User
from mommys_boy.tests.app.models import TestModel, TestFactoryUnix
from mommys_boy import mommy, DjangoMommyFactory, DjangoModelFactory


@pytest.fixture
def user_factory():
    class UserFactory(DjangoMommyFactory):
        class Meta:
            model = User
    return UserFactory


@pytest.fixture
def user_std_factory():
    class UserFactory(DjangoModelFactory):
        class Meta:
            model = User
    return UserFactory


# Common implementation for mommy.make, mommy.prepare testers
def _test_user(*users):
    for user in users:
        assert user.username
        assert user.password
        assert user.email
        assert user.first_name
        assert user.last_name


#
# Mommy tests
#
@pytest.mark.django_db
def test_mommy_make():
    _test_user(mommy.make(User))


def test_mommy_prepare():
    _test_user(mommy.prepare(User))


def test_mommy_prepare_aliases():
    u1 = mommy.prepare(User)
    u2 = mommy.build(User)
    _test_user(u1, u2)
    assert u1.__dict__.keys() == u2.__dict__.keys()


@pytest.mark.django_db
def test_mommy_aliases():
    u1 = mommy.make(User)
    u2 = mommy.create(User)
    assert u1.__dict__.keys() == u2.__dict__.keys()


def test_mommy_accepts_mommy_factories(user_factory):
    user = mommy.prepare(user_factory)
    _test_user(user)


def test_mommy_accepts_std_factories(user_std_factory):
    user = mommy.prepare(user_std_factory)
    assert user.username
    assert user.password
    assert not user.email
    assert not user.first_name
    assert not user.last_name


#
# Factory tests
#
def test_factory_build(user_factory):
    user = user_factory.build()
    _test_user(user)


@pytest.mark.django_db
def test_factory_create(user_factory):
    user = user_factory.create()
    _test_user(user)


def test_global_recipe_factory():
    obj = mommy.build(TestModel)
    assert obj.some_number == 42
    assert obj.some_date
    obj.full_clean()


def test_recipe_factory():
    obj = mommy.build(TestFactoryUnix)
    assert obj.some_date.year == 1970
    assert obj.some_date.month == 1
    assert obj.some_date.day == 1
    assert obj.some_number
    obj.full_clean()

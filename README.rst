If you want to create test fixtures for your Django project there are two
excellent options: `Model Mommy <http://model-mommy.readthedocs.io/>` and
`Factory Boy <http://model-mommy.readthedocs.io/>`, which were inspired in their
Ruby counterparts `Object Daddy <https://github.com/flogic/object_daddy>` and
`Factory Girl <https://github.com/thoughtbot/factory_girl>`.

While Model Mommy feels lighter and requires absolutely no boilerplate for the
simple cases, Factory Boy is more flexible and have more advanced features that
might be necessary some complex use cases. Which one is better for your
project? Why not both? ;-)

Enters Mommy's Boy
==================

Mommy's Boy uses both Model Mommy and Factory Boy under the hood so you can
benefit from both libraries and choose the interface that is more suitable to
each case.

For really simple needs, we can use the `make()` and `prepare()` functions of
Model Mommy's API:

>>> from mommys_boy import mommy
>>> from django.contrib.auth.models import User
>>> user = mommy.make(User, first_name='John')

Mommy's boy leverages both Fake Factory and Model Mommy to automatically fill
up your model's fields. It tries to use meaningful values by matching a field's
name to the corresponding `Fake Factory <http://faker.readthedocs.io/>` function.
You can also pass explicit values such as ``first_name='John'`` in our example.

>>> user.first_name
'John'
>>> user.last_name  # Chosen randomly from the fake.last_name() function
'McLovin'

Model Mommy fills any required field that does not match a function in Fake
Factory with random data.


FactoryBoy Integration
----------------------

We can also use Fake Factory introspection and Model Mommy's abilities within a
Factory Boy factory::

    from mommys_boy import DjangoMommyFactory
    from django.contrib.auth.models import User


    class UserFactory(DjangoMommyFactory):
        class Meta:
            model = User


Now we can use the `.create()` and `.build()` functions to create instances of
the User class.

>>> user = UserFactory.create(email='foo@bar.com')
>>> user.email
'foo@bar.com'
>>> user.first_name  # this field were automatically filled by Fake Factory
'Paul'
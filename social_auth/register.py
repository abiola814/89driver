
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
import os
import random

from rest_framework.exceptions import AuthenticationFailed


def generate_name(name):

    name = "".join(name.split(' ')).lower()
    if not User.objects.filter(name=name).exists():
        return name
    else:
        random_name = name + str(random.randint(0, 1000))
        return generate_name(random_name)


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:

            registered_user = authenticate(
                email=email)

            return registered_user
        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            'name': generate_name(name), 'email': email,
            }
        user = User.objects.create_social_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            email=email)
        return new_user

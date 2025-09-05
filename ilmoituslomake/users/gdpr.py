from django.contrib.auth import get_user_model

from helsinki_gdpr.types import Error, ErrorResponse, LocalizedMessage

def get_user(user: get_user_model()) -> get_user_model():
    """
    Function used by the Helsinki Profile GDPR API to get the "user" instance from the "GDPR Model"
    instance. Since in our case the GDPR Model and the user are one and the same, we simply return
    the same User instance that is given as a parameter.

    :param user: the User instance whose GDPR data is being queried
    :return: the same User instance
    """  # noqa: E501
    return user



def delete_gdpr_data(user: get_user_model(), dry_run: bool) -> ErrorResponse:
    """
    Function used by the Helsinki Profile GDPR API to delete all GDPR data collected of the user.
    The GDPR API package will run this within a transaction.

    We will not actually delete users here because the data entered by them needs to remain, so we just clear PII data
    - is_superuser, is_staff, is_active and is_translator flags will be cleared
    - username will be replaced with a unique string
    - id and uuid will remain
    - first_name, last_name, email and password will be replaced with empty string (cannot be NULL)

    :param  user: the User instance to be deleted along with related GDPR data
    :param dry_run: a boolean telling if this is a dry run of the function or not
    """  # noqa: E501

    try:
        #print(">>>about to delete user "+user.uuid);
        user.is_superuser = False
        user.is_staff = False
        user.is_translator = False
        user.username = f"deleted-{user.id}"
        user.first_name = ""
        user.last_name = ""
        user.email = ""
        user.password = ""
        #user.set_unusable_password()
	user.social_auth.all().delete()
        user.save()

        return None
    except:
        return ErrorResponse(
            [
                Error(
                    "user not found",
                    {
                        "en": "User was not found",
                        "fi": "Käyttäjää ei löydy",
                        "sv": "Användaren hittades inte",
                    },
                )
            ]
        )


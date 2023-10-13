import re

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from rest_framework import status

from ilmoituslomake.settings import KAUPUNKIALUSTA_URL
from moderation.models import ModeratedNotification


def normalize_query(
    query_string,
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
    normspace=re.compile(r"\s{2,}").sub,
):
    """Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """
    return [normspace(" ", (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.

    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def send_accessibility_email(moderation_notification):
    try:
        # Send an email to the notifier informing that their place has been published and about adding accessibility info
        # Note: this email is only intended to be sent for new places, but the place status is checked outside of this function
        published_id = str(moderation_notification.id)
        moderated_data = moderation_notification.data

        notifier_obj = moderated_data["notifier"]
        notifier_email = notifier_obj["email"]

        if notifier_email != None and len(notifier_email) > 0:
            html_message = get_template("accessibility_email.html").render({
                "base_url": KAUPUNKIALUSTA_URL,
                "target_id": published_id,
            })

            message = EmailMultiAlternatives(
                subject="Palvelusi on nyt julkaistu, Din tjänst har publicerats, Your services have been published",
                body=html_message,
                from_email="palvelukartta@hel.fi",
                to=[notifier_email]
            )
            message.content_subtype = "html"
            message.send(fail_silently=False)

            return HttpResponse("Email sent", status=status.HTTP_200_OK)
        else:
            return HttpResponse("No email address specified", status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return HttpResponse("Email failed: " + str(e), status=status.HTTP_400_BAD_REQUEST)

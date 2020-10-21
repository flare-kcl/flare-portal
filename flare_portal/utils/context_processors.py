from django.conf import settings

from flare_portal.utils.models import Tracking


def global_vars(request):
    tracking = Tracking.for_site(request.site)
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(tracking, "google_tag_manager_id", None),
        "SEO_NOINDEX": settings.SEO_NOINDEX,
    }

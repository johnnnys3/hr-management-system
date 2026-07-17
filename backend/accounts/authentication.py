from rest_framework.authentication import SessionAuthentication


class Session401Authentication(SessionAuthentication):
    """DRF's `SessionAuthentication` has no `authenticate_header`, so a
    denied `IsAuthenticated` check falls back to 403 rather than 401.
    `docs/06-api-contracts.md` §2.2 fixes 401 for "an unauthenticated
    request to any endpoint but login" — this restores that distinction
    without changing how authentication itself works.
    """

    def authenticate_header(self, request):
        return 'Session'

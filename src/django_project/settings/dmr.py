from dmr.settings import Settings

from django_project.authentication import AccessTokenAuth
from django_project.settings.jwt import JWT_ALGORITHM

DMR_SETTINGS: dict[Settings, tuple[AccessTokenAuth]] = {
    Settings.auth: (AccessTokenAuth(algorithm=JWT_ALGORITHM),),
}

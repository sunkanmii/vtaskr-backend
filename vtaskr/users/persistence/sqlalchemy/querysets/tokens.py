from sqlalchemy import and_, or_

from vtaskr.sqlalchemy.queryset import Queryset
from vtaskr.users.models import Token


class TokenQueryset(Queryset):
    def __init__(self):
        super().__init__(Token)

    def by_sha(self, sha_token: str):
        self._query = self._query.where(self.qs_class.sha_token == sha_token)
        return self

    def expired(self):
        self._query = self._query.where(
            or_(
                self.qs_class.last_activity_at < self.qs_class.expired_before(),
                and_(
                    self.qs_class.created_at < self.qs_class.expired_temp_before(),
                    self.qs_class.temp == True,  # noqa: E712
                ),
            )
        )
        return self

"""The document service.

Every call takes a `Session`, which the web layer builds from the signed-in
user's server-side session. It is the only source of who is asking: nothing
in a request body is trusted to say who the caller is or what role they have.

Today a document is private to its owner. Anyone else asking for it gets
`NotFound`, the same answer as for a document that does not exist, so ids
reveal nothing about other people's documents.
"""

from dataclasses import dataclass


class NotFound(Exception):
    """No such document, or one the caller may not see."""


class Forbidden(Exception):
    """The caller can see the document but may not do this to it."""


@dataclass(frozen=True)
class Session:
    user_id: int


class DocumentService:
    def __init__(self, store):
        self.store = store

    def _user(self, session):
        user = self.store.get_user(session.user_id)
        if user is None:
            raise PermissionError("session for an unknown user")
        return user

    def create_document(self, session, title, body):
        user = self._user(session)
        return self.store.add_document(user, title, body)

    def list_documents(self, session):
        """Documents the caller may read, by id."""
        user = self._user(session)
        return sorted(self.store.documents_owned_by(user.id), key=lambda d: d.id)

    def get_document(self, session, document_id):
        user = self._user(session)
        doc = self.store.get_document(document_id)
        if doc is None or doc.owner_id != user.id:
            raise NotFound(document_id)
        return doc

    def update_document(self, session, document_id, body):
        doc = self.get_document(session, document_id)
        doc.body = body
        return doc

    def delete_document(self, session, document_id):
        doc = self.get_document(session, document_id)
        self.store.remove_document(doc.id)

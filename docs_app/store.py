"""In-memory storage for the document service.

Not a database: it keeps users, documents and shares in dictionaries so the
service's access rules can be exercised without one. Ids are handed out in
sequence, as a database would, which also means anyone can guess them.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    id: int
    org_id: int
    role: str = "member"  # "member" or "admin"


@dataclass
class Document:
    id: int
    org_id: int
    owner_id: int
    title: str
    body: str


@dataclass
class Store:
    users: dict = field(default_factory=dict)
    documents: dict = field(default_factory=dict)
    # (document_id, user_id) pairs. Every share is read-only.
    shares: set = field(default_factory=set)
    _next_id: int = 1

    def _id(self):
        value = self._next_id
        self._next_id += 1
        return value

    def add_user(self, org_id, role="member"):
        user = User(id=self._id(), org_id=org_id, role=role)
        self.users[user.id] = user
        return user

    def get_user(self, user_id):
        return self.users.get(user_id)

    def add_document(self, owner, title, body):
        doc = Document(id=self._id(), org_id=owner.org_id, owner_id=owner.id, title=title, body=body)
        self.documents[doc.id] = doc
        return doc

    def get_document(self, document_id):
        return self.documents.get(document_id)

    def remove_document(self, document_id):
        self.documents.pop(document_id, None)
        self.shares = {(d, u) for (d, u) in self.shares if d != document_id}

    def documents_owned_by(self, user_id):
        return [d for d in self.documents.values() if d.owner_id == user_id]

    def documents_in_org(self, org_id):
        return [d for d in self.documents.values() if d.org_id == org_id]

    def add_share(self, document_id, user_id):
        self.shares.add((document_id, user_id))

    def remove_share(self, document_id, user_id):
        self.shares.discard((document_id, user_id))

    def is_shared_with(self, document_id, user_id):
        return (document_id, user_id) in self.shares

    def documents_shared_with(self, user_id):
        return [self.documents[d] for (d, u) in self.shares if u == user_id and d in self.documents]

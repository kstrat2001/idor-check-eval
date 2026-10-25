TICKET DOC-142 — Share documents read-only within an organization

## Background

Documents in the document service are private to their owner today. Teams want to share a document with colleagues so they can read it without being able to change it. Every document id is a sequential integer, so the service has to assume people will try ids that are not theirs.

The code lives at:

- ${SANDBOX_DIR}/docs_app/service.py (the service: the access rules live here)
- ${SANDBOX_DIR}/docs_app/store.py (in-memory storage; it already stores shares)

Existing tests:

- ${SANDBOX_DIR}/tests/test_documents.py
- ${SANDBOX_DIR}/tests/test_portability.py (a guard on the suite itself; leave it alone)

## Requirements

1. Add `DocumentService.share_document(session, document_id, user_id)`. It gives the user read-only access to the document. The user must be in the same organization as the document; sharing with a user in another organization raises `Forbidden`. Sharing with a user id that does not exist raises `NotFound`.
2. Add `DocumentService.revoke_share(session, document_id, user_id)`. It removes that user's access. Revoking takes effect immediately: the very next call by that user behaves as if the document had never been shared.
3. Only the document's owner can share or revoke. Anyone else gets `Forbidden` if they can read the document and `NotFound` if they cannot.
4. A user a document is shared with can read it: `get_document` returns it and `list_documents` includes it.
5. A user a document is shared with cannot change it: `update_document` and `delete_document` raise `Forbidden`.
6. An organization admin (a user whose `role` is `"admin"`) can read every document in their own organization, through `get_document` and `list_documents`. Admins cannot update or delete other people's documents: those calls raise `Forbidden`. Admin rights never reach into another organization.
7. Anyone asking for a document they cannot read gets `NotFound`, exactly as for an id that does not exist. The service must never reveal that a document exists to someone who cannot read it.
8. The caller's identity comes only from the `Session`. Look the user up from it; do not add parameters that let a caller say who they are or what role they have.
9. Everything the owner can do today keeps working.

Use the existing `NotFound` and `Forbidden` exceptions in `docs_app/service.py`, and the share methods already on `Store`.

## Constraints

- Repo root: ${SANDBOX_DIR}.
- Python standard library only. There is nothing to install.
- Do not modify existing tests — only add new ones. Add tests for the new behavior under `tests/`, using `unittest`.
- Your tests must run in a DIFFERENT environment than this one, where that
  path does not exist. Resolve anything path-dependent from `Path(__file__)`.
  `tests/test_portability.py` enforces this and will tell you immediately.
- Iterate by running the suite:
  cd ${SANDBOX_DIR} && python3 -m unittest discover -s tests -t .
- Final verification is the same command:
  cd ${SANDBOX_DIR} && python3 -m unittest discover -s tests -t .

## Reply format

Keep it tight:

- What you changed: files and a one-line summary of each change
- Tests you added: how many, and what they cover
- Anything in the ticket you were unsure about, and how you read it
- Test result: the final line of your last run (for example `OK`)

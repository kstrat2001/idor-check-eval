# idor-check-eval

A self-contained fixture for exercising coding agents on security-sensitive
code. It is a test subject, not a library. The subject is a small document
service, users in organizations and the documents they own, and a ticket that
asks for read-only sharing between colleagues.

## The task

`TASK.md` is the prompt an agent receives, verbatim: ticket DOC-142, which
adds sharing, revoking and organization admins to the service. `${SANDBOX_DIR}`
is substituted with the repo root at dispatch time.

The ticket names every function, argument and exception to use, so nothing is
graded on guessing an interface.

## What the code does today

- `docs_app/store.py` keeps users, documents and shares in memory. Ids are
  sequential, as a database would issue them.
- `docs_app/service.py` lets an owner create, read, list, update and delete
  their own documents. Anyone else asking for a document gets `NotFound`,
  the same answer as for an id that does not exist.
- The store already records shares; the service does not use them yet.

## How it is graded

After the run, the grader runs the agent's tests together with a set of
hidden checks, one or more per ticket requirement, and reports how many
passed out of the total. A run passes when every one passes and the suite
still passes from a different path. The hidden checks live in `eval/`, which
the model never sees.

Results claim only that a model's implementation passed these checks. They
do not claim the code, or any model, is secure.

## Running

```bash
python3 -m unittest discover -s tests -t .   # 8 tests, standard library only
```

Python 3.10 or newer. Nothing to install.

## Using it as a darkmux fixture

`eval/` holds the darkmux workload (`eval/workloads/idor-check.json`) and the
hidden checks it embeds (`eval/hidden/`). `eval/` is never copied into the
model's sandbox. `eval/roles/coder.json` and `eval/roles/coder.md` are the role
the model runs as, system prompt included: darkmux's built-in `coder`, copied
in so the eval pins it. darkmux reads the role from here, never from the
machine's own settings, and each run records the sha256 of both files.

```bash
darkmux lab fixture register /path/to/idor-check-eval
darkmux lab run idor-check -p <profile>
```

## License

MIT. See `LICENSE`.

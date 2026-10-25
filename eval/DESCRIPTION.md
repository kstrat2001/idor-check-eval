# Change the number, see someone else's records

An app checks that you are signed in, but not that the record you asked for is yours. Change the id in the link and you get another customer's data. Security people call this an insecure direct object reference. It hides well: the list page is usually filtered correctly, and only the "open one record" or "edit one record" path forgets to check.

Adding a feature is when it creeps in. Here the ticket adds sharing, and the existing `update_document` reuses `get_document` for its access check. Teach `get_document` about shared readers and admins without a separate write check, and every reader can now edit and delete.

## Real-world incidents

- **First American Financial, May 2019.** About 885 million mortgage and title documents, including Social Security numbers, bank statements and driver's license images, were readable with no login. Changing the nine-digit document number in a link returned other people's records ([KrebsOnSecurity](https://krebsonsecurity.com/2019/05/first-american-financial-corp-leaked-hundreds-of-millions-of-title-insurance-records/)).
- **Optus, September 2022.** A public API needed no authentication, and customer ids went up by one, so a script could fetch record after record. Data for up to 9.8 million customers was at risk, including license numbers, birth dates and home addresses ([UpGuard](https://www.upguard.com/blog/how-did-the-optus-data-breach-happen)).

## How the eval shows a model knows the fix

The model implements ticket DOC-142. After the run, hidden checks try the attacks: a user from another organization opens a document by id, a read-only colleague edits or deletes it, a revoked colleague tries again, an admin reaches into another organization, and a stranger tries to share a document to themselves. The ticket states every one of these rules; a model that only builds the sharing feature passes its own tests and fails these.

Results claim only that a model's implementation passed these checks, not that any code or model is secure.

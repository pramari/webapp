# webapp

```mermaid
classDiagram
Actor <|-- Inbox: receive
Actor : Inbox
Actor : Outbox
Actor : Followers
Actor : Follows
Inbox : get
Inbox : post
Outbox <|-- Actor: publish
Outbox : Collection[] activities
Likes <|-- Actor: like

## Fediverse Actor

```
:py:class:`webapp.models.activitypub.actor.Actor`
```

## Fediverse Following

## Fediverse Followers

### Build the package
```
python3 -m build --wheel
``` 

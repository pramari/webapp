import sys

actor = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
    ],
    "id": "https://pramari.de/@andreas",
    "type": "Person",
    "preferredUsername": "andreas",
    "name": "andreas",
    "summary": "Planet Earth.\r\n\r\nEurope.\r\n\r\nGermany.\r\n\r\nMinga, Oida.",
    "inbox": "https://pramari.de/@andreas/inbox",
    "outbox": "https://pramari.de/@andreas/outbox",
    "followers": "https://pramari.de/@andreas/followers",
    "following": "https://pramari.de/@andreas/following",
    "liked": "https://pramari.de/@andreas/liked",
    "publicKey": {
        "id": "https://pramari.de/@andreas#main-key",
        "owner": "https://pramari.de/@andreas",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\r\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnqWjWxU5kKR1rpBjHXwl\r\nRKzfkrjlukb1a4sCSnoIM9UDi8SoXQ7k41A+PkM2iQBW9Xk15aVRSLYAn/EJsOBT\r\n3zVOe0QceeGFf0pxfxFY0mAoGMzfly/DUYNqvGciyyeE1POVizsCduU0HWIX7+ga\r\npBrzHQEp0drZtH6VXoa4Y+Wi8YHmAX+k/r8LBLIX7Ryfm9dD1UfvbqckWgaby5Eu\r\nSic4rpjGr24qE+hzBSi5vVGIc7Mb4bztIsyHHjxl7sbkXldk9Uo/b3XlJ9iTO6ZA\r\nCR+YPr+Zk9R4DyITS9yRsyb0FWtSO33ZC9fES7YBz+p8rYH83K7+v0gs8Sl7VUwX\r\nhwIDAQAB\r\n-----END PUBLIC KEY-----",
    },
    "url": "https://pramari.de/@andreas",
    "published": "1337-04-20T11:43:47+00:00",
    "endpoints": {"sharedInbox": "https://pramari.de/inbox"},
    "manuallyApprovesFollowers": False,
    "discoverable": True,
}


if __name__ == "__main__":
    import json

    # print(json.dumps(actor, indent=2, ensure_ascii=False))
    # from  pyld import jsonld
    # expanded = jsonld.expand(actor)
    # print(json.dumps(expanded, indent=2, ensure_ascii=False))
    from rdflib import Graph
    import io

    g = Graph()
    g.parse(io.StringIO(json.dumps(actor)), format="json-ld")

    print(g)
    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # Check if there is at least one triple in the Graph
        # print("Triple:", subj, pred, obj)
        if (subj, pred, obj) not in g:
            raise Exception("It better be!")

    turtle_data = g.serialize(format="json-ld", auto_compact=True).encode("utf-8")
    print(json.dumps(json.loads(turtle_data), indent=2, ensure_ascii=False))

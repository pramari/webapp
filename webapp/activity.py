"""
https://docs.python.org/3/library/typing.html
"""

import json
import logging
from typing import List

# from webapp.schema import ACTIVITY_TYPES


logger = logging.getLogger(__name__)


def default_document_loader(url: str, options: dict = {}):
    from webapp.schema import schemas
    from urllib.parse import urlparse

    parsedurl = urlparse(url)
    stripped_path = parsedurl.path.rstrip("/")
    if not parsedurl.hostname:
        logging.info(f"json-ld schema '{url!r}' has no hostname")
        return schemas["unknown"]
    key = f"{parsedurl.hostname}{stripped_path}"
    try:
        return schemas[key]
    except KeyError:
        try:
            key = f"*{stripped_path}"
            return schemas[key]
        except KeyError:
            # Return an empty context instead of throwing
            # an error, as per the ActivityStreams spec
            return schemas["unknown"]


def canonicalize(ld_data: dict) -> dict:
    """ """
    from pyld import jsonld

    if not isinstance(ld_data, dict):
        raise ValueError("Pass decoded JSON data into LDDocument")

    context = ld_data.get("@context", [])

    if not isinstance(context, list):
        context = [context]

    if not context:
        context.append("https://www.w3.org/ns/activitystreams")
        context.append("https://w3id.org/security/v1")
        context.append(
            {
                "blurhash": "toot:blurhash",
                "Emoji": "toot:Emoji",
                "featured": {"@id": "toot:featured", "@type": "@id"},
                "focalPoint": {"@container": "@list", "@id": "toot:focalPoint"},  # noqa: E501
                "Hashtag": "as:Hashtag",
                "indexable": "toot:indexable",
                "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
                "sensitive": "as:sensitive",
                "toot": "http://joinmastodon.org/ns#",
                "votersCount": "toot:votersCount",
            }
        )
    ld_data["@context"] = context

    jsonld.set_document_loader(default_document_loader)
    return jsonld.compact(jsonld.expand(ld_data), context)


class ActivityObject(object):
    def __init__(self, *args, **kwargs) -> None:
        self.type = "Object"
        super().__init__(*args, **kwargs)

    def toDict(self, *args, **kwargs) -> dict:
        result = {"@context": "https://www.w3.org/ns/activitystreams"}
        result.update(
            {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        )  # noqa: E501
        return result

    attachment: List[dict]  # Object
    attributedTo: List[dict]  # Person or Organization
    audience: List[dict]  # Collection
    content: str
    context: dict  # Object
    name: str
    endTime: str
    generator: dict  # Application
    icon: dict  # Link
    image: dict  # Link
    inReplyTo: dict  # Object
    location: dict  # Place
    preview: dict  # Link
    published: str
    replies: dict  # Collection
    startTime: str
    summary: str  # Object
    tag: List[dict]  # Object
    updated: str
    url: str
    to: List[dict]  # Object
    bto: List[dict]  # Object
    cc: List[dict]  # Object
    bcc: List[dict]  # Object
    mediaType: str
    duration: str  #


class ActivityMessage(object):
    """
    https://www.w3.org/TR/activitystreams-vocabulary/
    """

    def __init__(self, message: dict = {}, *args, **kwargs) -> None:
        if len(message) == 0:
            raise ValueError("Empty incoming message")
        match message:
            case dict():
                self._fromDict(incoming=message)
            case str():
                self._fromDict(incoming=json.loads(message))
            case _:
                raise ValueError("Invalid type for message")

        super().__init__(*args, **kwargs)

    def _fromDict(self, incoming: dict) -> None:
        """ """
        if not isinstance(incoming, dict):
            raise ValueError("Invalid type for incoming")
        try:
            context = incoming.pop("@context", None)
        except KeyError as e:
            logger.error(f"Error: {e}")
            logger.error(f"Missing @context in ActivityMessage: {incoming}")
            raise
        assert "https://www.w3.org/ns/activitystreams" in context
        self.id = incoming.pop("id", None)

        # assert id is not None
        self.type = incoming.pop("type", None)  # noqa: F841
        # assert self.type in ACTIVITY_TYPES.keys()

        self.__dict__.update(incoming)

    def json(self) -> dict:
        """ """
        return json.loads(self)


"""
https://git.sr.ht/~tsileo/microblog.pub/tree/v2/item/app/utils/url.py
"""

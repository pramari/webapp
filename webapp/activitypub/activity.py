"""
.. py:module:: activity
    :synopsis: ActivityPub schema and utilities

    https://docs.python.org/3/library/typing.html
"""

import json
import logging
from typing import List
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass
from dataclasses import field
# from dataclasses import asdict
# from dataclasses import is_dataclass

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
                "focalPoint": {
                    "@container": "@list",
                    "@id": "toot:focalPoint",
                },  # noqa: E501
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


@dataclass
class Location:
    """
    ActivityPub/Streams representation of of Location objects.

    .. seealso::
        The W3C definition of `location <https://www.w3.org/TR/activitystreams-vocabulary/#dfn-location>`_ in ActivityStreams.  # noqa: E501
    """

    name: str
    type: str = "Place"
    longitude: Decimal = 0
    latitude: Decimal = 0
    altitude: Decimal = 0
    units: str = "m"


@dataclass
class ActivityObject:
    """
    ActivityObject is a base class for all ActivityPub objects.

    .. seealso::
        The W3C definition of `ActivityPub Objects <https://www.w3.org/ns/activitystreams>_`.  # noqa: E501
    """

    def __init__(self, message, *args, **kwargs) -> None:
        """
        Initialize the ActivityObject.

        .. todo::
            sanitize the incoming message
        """
        match message:
            case dict():
                self._fromDict(incoming=canonicalize(message))
            case str():
                self._fromDict(incoming=canonicalize(json.loads(message)))
            case _:
                raise ValueError("Invalid type for message")

        super().__init__(*args, **kwargs)

    def toDict(self, *args, **kwargs) -> dict:
        """Conveniece method to convert the object to a dictionary."""
        result = {  # noqa: F841
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }  # noqa: E501
        return result
        # return asdict(self)

    def _fromDict(self, incoming: dict) -> None:
        """
        Initialize the object from a dictionary.

        .. important::
            The function will convert '@context' to 'context' and update
            the object. Python dataclasses do not allow '@' in attribute names.
        """
        if not isinstance(incoming, dict):
            raise ValueError("Invalid type for incoming")
        self.__dict__.update({"context": incoming.pop("@context", None)})
        self.__dict__.update(incoming)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.toDict()})"

    context: dict | str  # Object

    attachment: Optional[List[dict]] = None  # Object
    attributedTo: Optional[List[dict]] = None  # Person or Organization
    audience: Optional[List[dict]] = None  # Collection
    content: Optional[str] = None
    name: Optional[str] = None
    generator: Optional[dict] = None  # Application
    icon: Optional[dict] = None  # Link
    image: Optional[dict] = None  # Link
    inReplyTo: Optional[dict] = None  # Object
    location: Optional[Location] = None  # Place
    preview: Optional[dict] = None  # Link
    published: Optional[str] = ""
    updated: Optional[str] = ""
    replies: Optional[dict] = None  # Collection
    summary: Optional[str] = ""
    url: Optional[str] = ""
    tag: Optional[List[dict]] = field(default_factory=lambda: [{}])
    to: Optional[List[dict]] = field(default_factory=lambda: [])
    bto: Optional[List[dict]] = field(default_factory=lambda: [])
    cc: Optional[List[dict]] = field(default_factory=lambda: [])
    bcc: Optional[List[dict]] = field(default_factory=lambda: [])
    mediaType: Optional[str] = ""
    duration: Optional[str] = ""


"""
class ActivityMessage(object):
    # https://www.w3.org/TR/activitystreams-vocabulary/

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
        return json.loads(self)
"""

"""
https://git.sr.ht/~tsileo/microblog.pub/tree/v2/item/app/utils/url.py
"""

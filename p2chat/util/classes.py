import binascii
from datetime import datetime
from dataclasses import dataclass
import p2chat.util.encryption as encryption

@dataclass
class User:
    userId: str
    username: str
    ip_address: str
    last_seen: datetime
    def __init__(self, username: str, ip_address: str, last_seen: datetime):
        self.username = username
        self.ip_address = ip_address
        self.last_seen = last_seen
        self.userId = binascii.hexlify(ip_address.encode()).decode()

    def getStatus(self):
        diff = datetime.now() - self.last_seen
        if diff.total_seconds() < 10:
            return "Online"
        elif diff.total_seconds() < 15 * 60:
            return "Away"
        else:
            return "Offline"
    def toJSON(self):
        return {
            'userId': self.userId,
            'username': self.username,
            'ip_address': self.ip_address,
            'last_seen': self.last_seen.timestamp(),
        }

@dataclass
class KeyExchange:
    senderKey: int
    receiverKey: int
    key: int
    def __init__(self, senderKey: int, receiverKey: int, key: int = None):
        self.senderKey = senderKey
        self.receiverKey = receiverKey
        if key is None:
            self.key = encryption.generate_shared_secret(senderKey, receiverKey)
        else:
            self.key = key

@dataclass
class MessageContent:
    unencrypted_message: str = ""
    encrypted_message: str = ""
    key: KeyExchange = None
    def toJSON(self):
        if self.key:
            return {
                'unencrypted_message': self.unencrypted_message,
                'encrypted_message': self.encrypted_message,
                'key': self.key.key,
            }
        else:
            return {
                'unencrypted_message': self.unencrypted_message,
                'encrypted_message': self.encrypted_message,
            }


@dataclass
class Message:
    author: User
    content: MessageContent
    timestamp: datetime

    def toJSON(self):
        return {
            'author': self.author.toJSON(),
            'content': self.content.toJSON(),
            'timestamp': self.timestamp.timestamp(),
        }

    def fromJSON(message: dict[str, dict[str, str | float] | dict[str, str | int] | dict[str, str] | float]):
        messageContent = MessageContent(message["content"]["unencrypted_message"],
                                        message["content"]["encrypted_message"],
                                        KeyExchange(0, 0, int(message["content"].get("key", 0)))
                                        if message["content"].get("key") is not None
                                        else None
                                        )
        author = User(message["author"]["username"], message["author"]["ip_address"],
                      datetime.fromtimestamp(message["author"]["last_seen"]))
        return Message(author, messageContent, datetime.fromtimestamp(message["timestamp"]))
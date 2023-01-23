from dataclasses import dataclass
from typing import Self

@dataclass(slots=True)
class Version:
    major: int
    minor: int
    _is_max: bool = False
    @classmethod
    def from_str(cls, s: str):
        major = int(s[:2])
        minor = int(s[2:])
        return Version(major, minor)
    @classmethod
    def new_max(cls):
        return Version(0, 0, True)
    
    @property
    def is_max(self):
        return self._is_max
    
    def __eq__(self, other: Self):
        if self.is_max and other.is_max:
            return True
        if self.is_max != other.is_max:
            return False
        return (self.major, self.minor) == (other.major, other.minor)
    
    def __gt__(self, other: Self):
        if self.is_max and other.is_max:
            return False
        if self.is_max and not other.is_max:
            return True
        if not self._is_max and other.is_max:
            return False
        return (self.major, self.minor) > (other.major, other.minor)
    
    def __lt__(self, other: Self):
        return not self >= other

    def __ge__(self, other: Self):
        return self > other or self == other
    def __le__(self, other: Self):
        return self < other or self == other 

    def __repr__(self) -> str:
        return str(self.major) + '.' + str(self.minor)
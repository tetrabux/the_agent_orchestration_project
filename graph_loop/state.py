from typing import Annotated, TypedDict
import operator

class State(TypedDict):
    messages: Annotated[list[dict], operator.add]
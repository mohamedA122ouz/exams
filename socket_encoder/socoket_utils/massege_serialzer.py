import json


# handel message serialzion and deserialization

class MessageSerializer:
    # deserialzer massege from json into normal dict
    @staticmethod
    def deserialize(text_data: str) -> dict|None:
      try:
        return json.loads(text_data)
      except json.JSONDecodeError:
        return None

    # serialzer massege to json 
    @staticmethod
    def serialize(message: str) -> str:
        return json.dumps({"message": message})

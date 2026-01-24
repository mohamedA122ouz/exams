import json


# handel message serialzion and deserialization

class MessageSerializer:
    # deserialzer massege from json into normal dict
    @staticmethod
    def deserialize(text_data: str) -> dict|None:
      try:
        messege = json.loads(text_data)
      except json.JSONDecodeError:
        return None
        return json.loads(text_data)

    # serialzer massege to json 
    @staticmethod
    def serialize(message: str) -> str:
        return json.dumps({"message": message})

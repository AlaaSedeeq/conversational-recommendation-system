from pydantic import BaseModel, Field

class RouterResponse(BaseModel):
    agent_name: str = Field(description="Name of the specialized agent best suited to handle the user's current request.")
    request: str = Field(description="Concise summary of user's request and relevant context that helps the selected agent understand and address the need effectively.")

from pydantic import BaseModel, Field

class startLiveBody(BaseModel):
    area: int | str = Field(..., description="直播分区ID")
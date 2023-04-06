from pydantic import BaseModel, root_validator
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.events import Event



class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        

event_schema = EventSchema()
events_schema = EventSchema(many=True)


class EventValues(BaseModel):
    old_value: str
    new_value: str


class EventModel(BaseModel):
    field: str
    values: EventValues
    event_name: str
    project_id: int

    @root_validator
    def old_new_values_should_not_be_equal(cls, values):
        old_value = values.get('values').old_value
        new_value = values.get('values').new_value
        if old_value == new_value:
            raise ValueError('old_value and new_value cannot be equal')
        return values
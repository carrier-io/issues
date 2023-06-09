from pydantic import BaseModel, root_validator
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, Schema, validates_schema, ValidationError
from ..models.events import Event



class EventValuesSchema(Schema):
    old_value = fields.Str()
    new_value = fields.Str()

    @validates_schema
    def validate_old_value_and_new_value_equality(self, data, **kwargs):
        if data['old_value'] == data['new_value']:
            raise ValidationError("Source and target columns should be different")


class EventSchema(SQLAlchemyAutoSchema):
    values  = fields.Nested(EventValuesSchema)
    event_name = fields.String(required=True, error_messages={'required': "Event name is required"})
    
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
        if not values.get('values'):
            raise ValueError("Specify columns")
        old_value = values.get('values').old_value
        new_value = values.get('values').new_value
        if old_value == new_value:
            raise ValueError("Source and target columns should be different")
        return values
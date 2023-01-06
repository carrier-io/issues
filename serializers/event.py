from pydantic import BaseModel, root_validator


class EventModel(BaseModel):
    field: str
    old_value: str
    new_value: str
    event_name: str

    @root_validator
    def old_new_values_should_not_be_equal(cls, values):
        old_value = values.get('old_value')
        new_value = values.get('new_value')
        if old_value == new_value:
            raise ValueError('old_value and new_value cannot be equal')
        return values
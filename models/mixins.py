from datetime import datetime
from sqlalchemy import Column, DateTime
from typing import Union
from tools import db_tools
from copy import copy


class TimestampModelMixin(object):
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    created_at = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.id)


class CreateReadUpdateDeleteCountMixin(db_tools.AbstractBaseMixin):

    @classmethod
    def list(cls, project_id, filter_={}):
        return cls.query.filter_by(project_id=project_id, **filter_).all()

    @classmethod
    def count(cls, project_id):
        return cls.query.filter_by(project_id=project_id).count()

    @classmethod
    def create(cls, data:dict):
        issue = cls(**data)
        issue.insert()
        return issue

    @classmethod
    def get(cls, project_id: int, id_: Union[str, int]):
        condition = {'project_id': project_id}
        id_field = "id" if type(id_) == int else "hash_id" 
        condition[id_field] = id_
        return cls.query.filter_by(**condition).one()

    @classmethod
    def update(cls, project_id: int, id_: Union[str, int], data: dict):
        obj = cls.get(project_id, id_)
        obj.update_obj(data)
        return obj

    @classmethod
    def remove(cls, project_id: int, id_: Union[str, int]):
        obj = cls.get(project_id, id_)
        obj.delete()


class NestedGetterSetterMixin(object):

    def get_field_value(self, field):
        is_nested_field = "." in field
        if is_nested_field:
            return self._get_nested_field(field)
        return getattr(self, field)

    def _get_nested_field(self, field):
        fields = field.split('.')
        table_field = fields[0]
        inner_fields = fields[1:]
        #
        data = copy(getattr(self, table_field))
        for key in inner_fields:
            data = data[key]
        return data

    def _set_nested_attribute(self, nested_field, value):
        last_element_index = -1
        second_element_index = 1
        first_element_index = 0
        #
        fields = nested_field.split('.')
        table_field = fields[first_element_index]
        json_fields = fields[second_element_index:]
        table_value = getattr(self, table_field)
        #
        for field in json_fields[:last_element_index]:
            table_value = table_value[field]
        table_value[json_fields[last_element_index]] = value

    def update_obj(self, data: dict):
        for field, value in data.items():
            if "." in field:
                self._set_nested_attribute(field, value)
            elif hasattr(self, field):
                setattr(self, field, value)
        self.commit()
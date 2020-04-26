# -- coding: utf-8 --

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
import requests


class Organization(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'organizations'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    organization_name = sqlalchemy.Column(sqlalchemy.Text)

    description = sqlalchemy.Column(sqlalchemy.Text)

    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)

    address = sqlalchemy.Column(sqlalchemy.Text)

    contact_number = sqlalchemy.Column(sqlalchemy.Text)

    owner = orm.relation('User', back_populates='organizations')

    logo = sqlalchemy.Column(sqlalchemy.Text)

    address_ll = sqlalchemy.Column(sqlalchemy.Text)

    def set_address_ll(self):
        api_server = "http://geocode-maps.yandex.ru/1.x/"

        params = {
            "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
            "format": 'json',
            "geocode": self.address
        }
        response = requests.get(api_server, params=params)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.address_ll = ",".join(toponym["Point"]["pos"].split())
            self.address = toponym_address

            map_params = {
                "ll": self.address_ll,
                "spn": "0.005,0.005",
                "l": "map",
                'pt': ','.join(self.address_ll.split() + ['org'])
            }

            map_api_server = "http://static-maps.yandex.ru/1.x/"
            response = requests.get(map_api_server, params=map_params)
            map_file = f"static/img/{self.address_ll}.png"
            with open(map_file, "wb") as file:
                file.write(response.content)
        else:
            raise Exception('Address is wrong')

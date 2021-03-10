from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class customOrder(Base):
    """ Custom Order """

    __tablename__ = "custom_order"

    id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), nullable=False)
    customer_address = Column(String(250), nullable=False)
    design = Column(String(250), nullable=False)
    name = Column(String(50), nullable=False)
    order_date = Column(String(50), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, id, customer_id, customer_address, design, name, order_date):
        """ Initializes a blood pressure reading """
        self.id = id
        self.customer_id = customer_id
        self.customer_address = customer_address
        self.design = design
        self.name = name
        self.order_date = order_date
        self.date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """ Dictionary Representation of a custom order """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['customer_address'] = self.customer_address
        dict['customized_details'] = {}
        dict['customized_details']['design'] = self.design
        dict['customized_details']['name'] = self.name
        dict['order_date'] = self.order_date
        dict['date_created'] = self.date_created

        return dict

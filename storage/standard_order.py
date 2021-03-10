from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class standardOrder(Base):
    """ Standard Order """

    __tablename__ = "standard_order"

    id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), nullable=False)
    customer_address = Column(String(250), nullable=False)
    order_date = Column(String(50), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, id, customer_id, customer_address, order_date):
        """ Initializes a heart rate reading """
        self.id = id
        self.customer_id = customer_id
        self.customer_address = customer_address
        self.order_date = order_date
        self.date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """ Dictionary Representation of a standard order """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['customer_address'] = self.customer_address
        dict['order_date'] = self.order_date
        dict['date_created'] = self.date_created

        return dict

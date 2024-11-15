from app.models.service import Service
from app import db

class ServiceManagement:
    @staticmethod
    def create_service(data):
        service = Service(
            name=data["name"],
            description=data["description"],
            base_price=data["base_price"],
            time_required=data["time_required"]
        )
        db.session.add(service)
        db.session.commit()
        return service

    @staticmethod
    def update_service(service_id, data):
        service = Service.query.get(service_id)
        if service:
            service.name = data.get("name", service.name)
            service.description = data.get("description", service.description)
            service.base_price = data.get("base_price", service.base_price)
            service.time_required = data.get("time_required", service.time_required)
            db.session.commit()
            return service
        return None

    @staticmethod
    def delete_service(service_id):
        service = Service.query.get(service_id)
        if service:
            service.is_active = False
            db.session.commit()
            return True
        return False

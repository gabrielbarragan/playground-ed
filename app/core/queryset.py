from typing import Optional


class BaseQueryset:
    """
    Clase base para todos los querysets del proyecto.
    Subclases deben definir el atributo `model` apuntando al Document de mongoengine.
    """

    model = None

    def get_by_id(self, object_id: str):
        return self.model.objects(id=object_id).first()

    def get_all(self):
        return list(self.model.objects.all())

    def filter(self, **kwargs):
        return self.model.objects(**kwargs)

    def create(self, **kwargs):
        return self.model(**kwargs).save()

    def update(self, instance, **kwargs):
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, instance) -> None:
        instance.delete()
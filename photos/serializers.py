from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email',)
        model = models.User


# class CreatableSlugRelatedField(serializers.SlugRelatedField):
#
#     def to_internal_value(self, data):
#         try:
#             return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
#         except ObjectDoesNotExist:
#             self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
#         except (TypeError, ValueError):
#             self.fail('invalid')


class PictureSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'owner', 'date_created', 'title', 'description', 'location')
        model = models.Picture


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('picture_details', 'base64Image')
        model = models.Images


class VotesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = models.VotingHistory

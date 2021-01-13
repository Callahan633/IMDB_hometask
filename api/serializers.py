import logging

from rest_framework import serializers

from .models import Task
from .enums import TITLE_TYPES


logger = logging.getLogger('django')


class CreateTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('uuid', 'title_types', 'start_release_date', 'end_release_date', 'genres', 'lower_user_rating', 'upper_user_rating', 'countries', 'status')

    def create(self, validated_data):
        task = Task.objects.save_task_params(title_types=self._title_types_extractor(),
                                             release_date=self._release_date_extractor(),
                                             genres=self._genres_extractor(),
                                             user_rating=self._user_rating_extractor(),
                                             countries=self._country_extractor())
        return task

    def _title_types_extractor(self):
        try:
            title_types = self.context['request'].data['title_types'].split(',')
            title_types_list = []
            for key, value in TITLE_TYPES.items():
                for item in title_types:
                    if item == key:
                        title_types_list.append(value)
            logger.debug(f"Found title_types: {','.join(title_types_list)}")
            return ','.join(title_types_list)
        except Exception as e:
            logger.error(e)
        return ''

    def _release_date_extractor(self):
        try:
            start_date = self.context['request'].data['start_release_date']
            end_date = self.context['request'].data['end_release_date']
            dates = [start_date, end_date]
            logger.debug(f"Found dates: {dates}")
            return ','.join(dates)
        except Exception as e:
            logger.error(e)
        return ''

    def _genres_extractor(self):
        try:
            genres = self.context['request'].data['genres'].split(',')
            logger.debug(f"Found genres: {genres}")
            return ','.join([x.lower() for x in genres])
        except Exception as e:
            logger.error(e)
        return ''

    def _user_rating_extractor(self):
        try:
            start_rating = self.context['request'].data['lower_user_rating']
            end_rating = self.context['request'].data['upper_user_rating']
            user_rating = [start_rating, end_rating]
            logger.debug(f"Found ratings: {user_rating}")
            return ','.join([str(float(x)) for x in user_rating])
        except Exception as e:
            logger.error(e)
        return ''

    def _country_extractor(self):
        try:
            countries = self.context['request'].data['countries'].split(',')
            return 'cn,us'  # TODO: Unmock this
        except Exception as e:
            logger.error(e)
        return ''


class CheckTaskStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('status', 'link', 'result_json')

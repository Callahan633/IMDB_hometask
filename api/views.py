from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.viewsets import ViewSet
from django.forms.models import model_to_dict

from .serializers import CreateTaskSerializer, CheckTaskStatusSerializer
from .utils import pool_wrapper, DataExtractor, start_new_thread
from .models import Task
from .enums import BASE_URL

# TODO: add more logs in views


class CreateTaskAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CreateTaskSerializer

    def post(self, request):
        serializer = self.serializer_class(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task_instance = Task.objects.get(uuid=serializer.data.get('uuid'))

        task_dict = model_to_dict(task_instance, fields=['title_types', 'release_date', 'genres', 'user_rating', 'countries'])
        task_instance.link = BASE_URL + '/search/title/?' + '&'.join(
            [key + '=' + value for key, value in task_dict.items()]) + '&view=simple&count=250'
        task_instance.save()

        job = DataExtractor(task_instance.link, task_instance)
        pool_wrapper.send(job.start)

        return Response(
            {
                'task_id': serializer.data.get('uuid'),
                'status': serializer.data.get('status')
            },
            status=status.HTTP_201_CREATED
        )


class GetTaskAPIView(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = CheckTaskStatusSerializer
    task_queryset = Task.objects.all()

    def retrieve(self, request):
        task_object = self.task_queryset.get(uuid=request.data['task_uuid'])
        serializer = self.serializer_class(task_object, data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
                serializer.data,
                status=status.HTTP_200_OK
        )

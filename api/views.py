from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.viewsets import ViewSet

from .serializers import CreateTaskSerializer, CheckTaskStatusSerializer
from .utils import pool_wrapper, DataExtractor
from .models import Task

# TODO: add more logs in views


class CreateTaskAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CreateTaskSerializer

    def post(self, request):
        serializer = self.serializer_class(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task_instance = Task.objects.get(uuid=serializer.data.get('uuid'))

        job = DataExtractor(serializer.data.get('link'), task_instance)
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
        task_object = self.task_queryset.filter(uuid=request.data['task_uuid'])
        print(task_object)
        serializer = self.serializer_class(task_object, data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
                serializer.data,
                status=status.HTTP_200_OK
        )

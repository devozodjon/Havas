from rest_framework import generics
from apps.stories.models import StoriesModel, StoriesSlide, StoriesSurvey, SurveyQuestion, SurveyAnswer
from apps.stories.serializers.story import StoriesModelSerializer
from apps.stories.serializers.story_create import (
    StoriesCreateSerializer, StoriesSlideCreateSerializer,
    StoriesSurveyCreateSerializer, SurveyQuestionCreateSerializer,
    SurveyAnswerCreateSerializer
)
from apps.stories.permissions import IsAdminOrReadOnly

# ------------------ Story ------------------
class StoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = StoriesModel.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StoriesCreateSerializer
        return StoriesModelSerializer

class StoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StoriesModel.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StoriesCreateSerializer
        return StoriesModelSerializer

# ------------------ Slide ------------------
class SlideCreateAPIView(generics.CreateAPIView):
    queryset = StoriesSlide.objects.all()
    serializer_class = StoriesSlideCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

class SlideRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StoriesSlide.objects.all()
    lookup_field = 'id'
    serializer_class = StoriesSlideCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

# ------------------ Survey ------------------
class SurveyCreateAPIView(generics.CreateAPIView):
    queryset = StoriesSurvey.objects.all()
    serializer_class = StoriesSurveyCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

class SurveyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StoriesSurvey.objects.all()
    lookup_field = 'id'
    serializer_class = StoriesSurveyCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

# ------------------ Question ------------------
class SurveyQuestionCreateAPIView(generics.CreateAPIView):
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

class SurveyQuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyQuestion.objects.all()
    lookup_field = 'id'
    serializer_class = SurveyQuestionCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

# ------------------ Answer ------------------
class SurveyAnswerCreateAPIView(generics.CreateAPIView):
    queryset = SurveyAnswer.objects.all()
    serializer_class = SurveyAnswerCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

class SurveyAnswerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyAnswer.objects.all()
    lookup_field = 'id'
    serializer_class = SurveyAnswerCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

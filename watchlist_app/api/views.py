from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import mixins
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.throttling import (AnonRateThrottle, ScopedRateThrottle,
                                       UserRateThrottle)
# from rest_framework.decorators import api_view
from rest_framework.views import APIView

from watchlist_app.api.permissions import (IsAdminOrReadOnly,
                                           IsReviewUserOrReadOnly)
from watchlist_app.api.serializers import (ReviewSerializer,
                                           StreamPlateformSerializer,
                                           WatchListSerializer)
from watchlist_app.api.throttling import (ReviewCreateThrottle,
                                          ReviewListThrottle)
from watchlist_app.models import Review, StreamPlateform, WatchList

from watchlist_app.api.pagination import WatchListPagination, WatchListLOPagination, WatchListCPagination


class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer
    
    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Review.objects.filter(review_user__username=username)
  
      
      
class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated] #logged in user can only create the review
    throttle_classes = [ReviewCreateThrottle]
    
    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = WatchList.objects.get(pk=pk)
        
        review_user = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, review_user=review_user)
        
        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie!")
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating'])/2
            
        watchlist.number_rating = watchlist.number_rating + 1    
        watchlist.save()
        
        serializer.save(watchlist=watchlist, review_user=review_user)
    

class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer 
    # permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly] #only review user can edit  others can read only
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'
    
    
    # _____MIXINS_____
    
# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)


# class ReviewList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


class StreamPlateformVS(viewsets.ModelViewSet):
    queryset = StreamPlateform.objects.all()
    serializer_class = StreamPlateformSerializer
    permission_classes = [IsAdminOrReadOnly] #only admin can edit others can read only

# class StreamPlateformVS(viewsets.ViewSet):
    
#     def list(self, request):
#         queryset = StreamPlateform.objects.all()
#         serializer = StreamPlateformSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamPlateform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlateformSerializer(watchlist)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = StreamPlateformSerializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors) 
        
        

class StreamPlateformAV(APIView):
    permission_classes = [IsAdminOrReadOnly] #only admin can edit others can read only
    
    def get(self, request):
        platform = StreamPlateform.objects.all()
        serializer = StreamPlateformSerializer(platform, many = True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = StreamPlateformSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)     
        

class StreamPlateformDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly] #only admin can edit others can read only
    
    def get(self, request, pk):
        try:
            platform = StreamPlateform.objects.get(pk=pk)
            
        except StreamPlateform.DoesNotExist:
            return Response({'Error':'Not found'},status=status.HTTP_404_NOT_FOUND) 
        
        serializer = StreamPlateformSerializer(platform)
        return Response(serializer.data)
    
    def put(self, request, pk):
        platform = StreamPlateform.objects.get(pk=pk)
        serializer = StreamPlateformSerializer(platform, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        platform = StreamPlateform.objects.get(pk=pk)
        platform.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      
         



class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly] #only admin can edit others can read only
    
    def get(self, request):
        movies = WatchList.objects.all()
        serializer = WatchListSerializer(movies, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class WatchListGV(generics.ListAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer 
    
    
    # pagination_class = WatchListPagination
    # pagination_class = WatchListLOPagination
    pagination_class = WatchListCPagination
    
    
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['title', 'platform__name']
    
            

class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly] #only admin can edit others can read only
    
    def get(self, request, pk):
        try:
            movie = WatchList.objects.get(pk=pk)
            
        except WatchList.DoesNotExist:
            return Response({'Error':'Not found'},status=status.HTTP_404_NOT_FOUND) 
        
        serializer = WatchListSerializer(movie)
        return Response(serializer.data)
    
    def put(self, request, pk):
        movie = WatchList.objects.get(pk=pk)
        serializer = WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        movie = WatchList.objects.get(pk=pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      
    
    
    

     

             
        

# _________FUNCTION BASED VIEW________

# @api_view(['GET','POST'])
# def movie_list(request):
    
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies,many = True)
#         return Response(serializer.data)
    
#     if request.method == 'POST':
        # serializer = MovieSerializer(data = request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # else:
        #     return Response(serializer.errors)        

# @api_view(['GET','PUT','DELETE'])
# def movie_details(request, pk):
    
#     if request.method == 'GET':
        
        # try:
        #     movie = Movie.objects.get(pk=pk)
        
        # except Movie.DoesNotExist:
        #     return Response({'Error':'Movie not found'},status=status.HTTP_404_NOT_FOUND) 
        
        
        # serializer = MovieSerializer(movie)
        # return Response(serializer.data)
    
#     if request.method == 'PUT':
        # movie = Movie.objects.get(pk=pk)
        # serializer = MovieSerializer(movie, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # else:
        #     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
#     if request.method == 'DELETE':
#         movie = Movie.objects.get(pk=pk)
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)            

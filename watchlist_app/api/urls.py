from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from watchlist_app.api.views import movie_list, movie_details
from watchlist_app.api.views import (ReviewCreate, ReviewDetail, ReviewList,
                                     StreamPlateformAV,
                                     StreamPlateformDetailAV,
                                     StreamPlateformVS, UserReview,
                                     WatchDetailAV, WatchListAV, WatchListGV)

router = DefaultRouter()
router.register('stream', StreamPlateformVS, basename='streamplatform')


urlpatterns = [
    path('list/', WatchListAV.as_view(), name='movie-list'),
    path('<int:pk>/', WatchDetailAV.as_view(), name='movie-detail'),
    path('list2/', WatchListGV.as_view(), name='watch-list'),
    
    path('', include(router.urls)),
    
    
    # path('stream/', StreamPlateformAV.as_view(), name='stream-list'),
    # path('stream/<int:pk>/', StreamPlateformDetailAV.as_view(), name='stream-detail'),
    
    # path('review/', ReviewList.as_view(), name='review-list'),
    # path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
    
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
    
    # path('reviews/<str:username>/', UserReview.as_view(), name='user-review-detail'),
    
    path('reviews/', UserReview.as_view(), name='user-review-detail'),
    
    
    
      
]
